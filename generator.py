from llvmlite import ir, binding
from element import SentenceType, ExpressionType, ConditionType
from tokens import BinaryOperator, Word
from ctypes import CFUNCTYPE


class VariableUndefinedError(Exception):

    def __init__(self, identifier):
        self.identifier = identifier


class FunctionUndefinedError(Exception):

    def __init__(self, identifier):
        self.identifier = identifier


class IRGenerator(object):

    def __init__(self, program):
        self.module = ir.Module('main')
        self.program = program
        self.engine = None

    def emit_procedure(self, procedure):
        identifier, subprogram = procedure

        try:
            existing_func = self.module.get_global(identifier)
            return existing_func
        except KeyError:
            pass

        fnty = ir.FunctionType(ir.VoidType(), ())
        func = ir.Function(self.module, fnty, identifier)

        block = func.append_basic_block('entry')
        builder = ir.IRBuilder(block)

        self.emit_subprogram(subprogram.content, builder)
        builder.ret_void()

        return func

    def emit_printf(self):
        try:
            existing_func = self.module.get_global('printf')
            return existing_func
        except KeyError:
            pass

        fnty = ir.FunctionType(ir.IntType(32), (ir.PointerType(ir.IntType(8)),), var_arg=True)
        func = ir.Function(self.module, fnty, 'printf')

        return func

    def emit_scanf(self):
        try:
            existing_func = self.module.get_global('scanf')
            return existing_func
        except KeyError:
            pass

        fnty = ir.FunctionType(ir.IntType(32), (ir.PointerType(ir.IntType(8)),), var_arg=True)
        func = ir.Function(self.module, fnty, 'scanf')

        return func

    def emit_subprogram(self, program, builder):
        consts = {}
        if program.consts is not None:
            for const in program.consts.content:
                identifier, value = const
                consts[identifier] = ir.Constant(ir.IntType(64), value)

        variables = {}
        if program.variables is not None:
            for variable in program.variables.content:
                variable_ptr = builder.alloca(ir.IntType(64), name=variable)
                variables[variable] = variable_ptr

        for procedure in program.procedures:
            self.emit_procedure(procedure)

        self.emit_sentence(program.sentence, builder, consts, variables)

    def emit_sentence(self, sentence, builder, consts, variables):
        if sentence.type == SentenceType.ASSIGN:
            identifier, expression = sentence.content

            ptr = variables.get(identifier, None)
            if ptr is None:
                try:
                    ptr = self.module.get_global(identifier)
                except KeyError:
                    raise VariableUndefinedError

                if ptr.global_constant:
                    raise VariableUndefinedError

            expression_ptr = self.emit_expression(expression, builder, consts, variables)
            return builder.store(expression_ptr, ptr)
        elif sentence.type == SentenceType.CALL:
            identifier = sentence.content

            try:
                func = self.module.get_global(identifier)
            except KeyError:
                raise FunctionUndefinedError(identifier)

            return builder.call(func, ())
        elif sentence.type == SentenceType.CONDITION:
            condition, sentence = sentence.content

            if sentence is None:
                return

            with builder.if_then(self.emit_condition(condition, builder, consts, variables)) as if_then:
                self.emit_sentence(sentence, builder, consts, variables)

            return if_then
        elif sentence.type == SentenceType.LOOP:
            condition, sentence = sentence.content

            while_block = builder.append_basic_block(builder.block.name + '.whilecondition')
            then_block = builder.append_basic_block(builder.block.name + '.whilethen')
            end_while_block = builder.append_basic_block(builder.block.name + '.endwhile')

            builder.branch(while_block)
            builder.position_at_start(while_block)
            builder.cbranch(self.emit_condition(condition, builder, consts, variables), then_block, end_while_block)

            builder.position_at_start(then_block)
            self.emit_sentence(sentence, builder, consts, variables)
            builder.branch(while_block)

            builder.position_at_start(end_while_block)
        elif sentence.type == SentenceType.WRITE:
            expressions = sentence.content

            format = ' '.join('%i' for _ in range(len(expressions))) + '\n\00'
            format_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(format)), bytearray(format.encode('ascii')))
            format_var = builder.alloca(ir.ArrayType(ir.IntType(8), len(format)))
            builder.store(format_const, format_var)
            format_ptr = builder.bitcast(format_var, ir.IntType(8).as_pointer())

            printf = self.emit_printf()
            builder.call(printf, [format_ptr] + [self.emit_expression(expression, builder, consts, variables) for expression in expressions])
        elif sentence.type == SentenceType.READ:
            identifiers = sentence.content

            format = ' '.join('%i' for _ in range(len(identifiers))) + '\00'
            format_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(format)), bytearray(format.encode('ascii')))
            format_var = builder.alloca(ir.ArrayType(ir.IntType(8), len(format)))
            builder.store(format_const, format_var)
            format_ptr = builder.bitcast(format_var, ir.IntType(8).as_pointer())

            scanf = self.emit_scanf()
            builder.call(scanf, [format_ptr] + [self.module.get_global(identifier) for identifier in identifiers])
        elif sentence.type == SentenceType.COMPOUND:
            sentences = sentence.content

            return [self.emit_sentence(sub_sentence, builder, consts, variables) for sub_sentence in sentences]

    def emit_expression(self, expression, builder, consts, variables):
        if expression.type == ExpressionType.NUMBER:
            value = expression.content
            return ir.Constant(ir.IntType(64), value)
        elif expression.type == ExpressionType.IDENTIFIER:
            identifier = expression.content
            variable = consts.get(identifier, None)
            if variable is None:
                variable = variables.get(identifier, None)
            if variable is None:
                variable = self.module.get_global(identifier)

            value = builder.load(variable)

            return value
        elif expression.type == ExpressionType.BINARY:
            lhs, operator, rhs = expression.content
            lhs_expression = self.emit_expression(lhs, builder, consts, variables)
            rhs_expression = self.emit_expression(rhs, builder, consts, variables)

            if operator == BinaryOperator.PLUS:
                return builder.add(lhs_expression, rhs_expression)
            elif operator == BinaryOperator.MINUS:
                return builder.sub(lhs_expression, rhs_expression)
            elif operator == BinaryOperator.TIMES:
                return builder.mul(lhs_expression, rhs_expression)
            elif operator == BinaryOperator.SLASH:
                return builder.sdiv(lhs_expression, rhs_expression)

    def emit_condition(self, condition, builder, consts, variables):
        if condition.type == ConditionType.UNARY:
            word, expression = condition.content
            assert word == Word.ODD
            result = self.emit_expression(expression, builder, consts, variables)
            return builder.trunc(result, ir.IntType(1))
        elif condition.type == ConditionType.BINARY:
            lhs, operator, rhs = condition.content
            lhs_result = self.emit_expression(lhs, builder, consts, variables)
            rhs_result = self.emit_expression(rhs, builder, consts, variables)

            if operator == BinaryOperator.EQUAL:
                return builder.icmp_signed('==', lhs_result, rhs_result)
            elif operator == BinaryOperator.HASHTAG:
                return builder.icmp_signed('!=', lhs_result, rhs_result)
            elif operator == BinaryOperator.LESS:
                return builder.icmp_signed('<', lhs_result, rhs_result)
            elif operator == BinaryOperator.LESSEQUAL:
                return builder.icmp_signed('<=', lhs_result, rhs_result)
            elif operator == BinaryOperator.GREATER:
                return builder.icmp_signed('>', lhs_result, rhs_result)
            elif operator == BinaryOperator.GREATEREQUAL:
                return builder.icmp_signed('>=', lhs_result, rhs_result)

    def emit(self):
        if self.program.consts is not None:
            for const in self.program.consts.content:
                identifier, value = const
                constant = ir.GlobalVariable(self.module, ir.IntType(64), identifier)
                constant.global_constant = True
                constant.initializer = ir.Constant(ir.IntType(64), value)

        if self.program.variables is not None:
            for variable in self.program.variables.content:
                var = ir.GlobalVariable(self.module, ir.IntType(64), variable)
                var.initializer = ir.Constant(ir.IntType(64), 0)

        for procedure in self.program.procedures:
            self.emit_procedure(procedure.content)

        fnty = ir.FunctionType(ir.VoidType(), ())
        func = ir.Function(self.module, fnty, 'main')

        block = func.append_basic_block('entry')
        builder = ir.IRBuilder(block)

        self.emit_sentence(self.program.sentence, builder, {}, {})
        builder.ret_void()

    def generate(self):
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        backing_mod = binding.parse_assembly('')
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)

        mod = binding.parse_assembly(str(self.module))
        mod.verify()

        engine.add_module(mod)
        engine.finalize_object()

        self.engine = engine

    def run(self):
        func_ptr = self.engine.get_function_address('main')
        func = CFUNCTYPE(None)(func_ptr)
        func()
