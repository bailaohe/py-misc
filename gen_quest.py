import random
import time
import click
from docx import Document

OP_TABLE = ['+', '-', '×']

def gen_question(qnum:int, with_answer:bool=False):
    """gen_question

    :param qnum: the count to questions
    :type qnum: int
    """
    random.seed(time.time())
    for i in range(qnum):
        first = random.randint(0, 10)
        op = OP_TABLE[random.randint(0, 1)]
        if op == '+':
            second = random.randint(first, 10) - first
        elif op == '-':
            second = random.randint(0, first)
        if with_answer:
            answer = (first + second) if op == '+' else \
                     (first - second) if op == '-' else \
                     (first * second) if op == '×' else \
                     0
            yield '%2d %1s%2d = %2d' % (first, op, second, answer)
        else:
            yield '%2d %1s%2d =' % (first, op, second)

class DocxExporter(object):
    """DocxExporter"""
    def open(self, path, columns=2):
        """open the docx exporter

        :param path: the path to dump docx file
        :param columns: the columns of exported docx file
        """
        doc = Document()
        # set a normal monsopaced font
        doc.styles['Normal'].font.name = u'Courier New'
        qtable = doc.add_table(rows=0, cols=columns)
        return (doc, qtable, path)

    def write(self, handle, qrow):
        """write the question row into the docx handle

        :param handle: the handle of open handle of docx exporter
        :param qrow: the question row
        """
        (_, qtable, _) = handle
        qcells = qtable.add_row().cells
        for qid, qtext in enumerate(qrow):
            qcells[qid].text = qtext

    def close(self, handle):
        """close the handle of docx handle

        :param handle: the handle
        """
        (doc, _, path) = handle
        doc.save(path)

class PlainExporter(object):
    """PlainExporter"""
    EXPR_WIDTH = 11
    LINE_WIDTH = 84

    def open(self, path, columns=2):
        """open the plain exporter

        :param path: the path (useless)
        :param columns: the columns to dump questions
        """
        return (columns,)

    def write(self, handle, qrow):
        """write the question row

        :param handle: the plain handle
        :param qrow: the question row
        """
        (columns,) = handle
        qline = ''
        for qid in range(columns - 1):
            qline += qrow[qid]
            qline += ' ' * int(PlainExporter.LINE_WIDTH / columns - PlainExporter.EXPR_WIDTH)
        qline += qrow[columns - 1]
        print(qline)

    def close(self, handle):
        """close the plain handle

        :param handle: the plain handle
        """
        pass

# the registerred exporters
EXPRORTERS = {
    'docx': DocxExporter,
    'doc': DocxExporter,
    'plain': PlainExporter,
}

@click.command()
@click.option('-q', '--questions', default=100, show_default=True, help='出题数量')
@click.option('-c', '--columns', default=2, show_default=True, help='输出列数')
@click.option('-e', '--export-format', default='plain', type=click.Choice(['plain', 'doc', 'docx']), show_default=True, help='导出类型')
@click.option('-f', '--export-name', default='quest', show_default=True, help='导出文件名')
@click.option('--with-answer/--without-answer', default=False, help='是否导出答案')
def gqcmd(questions, columns, export_format, export_name, with_answer):
    """gqcmd the command entry to generate questions

    :param columns: the column count
    :param questions: the question count
    :param export_format: the export format
    :param export_name: the export file name
    :param with_answer: answer the question or not
    """
    exporter = EXPRORTERS[export_format]()
    ehandle = exporter.open(export_name + '.' + export_format, columns=columns)

    # the row to hold questions in single row
    qrow = list()
    for q in gen_question(questions, with_answer):
        qrow.append(q)
        # trigger the row dump whenever the it is *FULL*
        if len(qrow) >= columns:
            exporter.write(ehandle, qrow)
            qrow = list()
    exporter.close(ehandle)

if __name__ == '__main__':
    gqcmd()

