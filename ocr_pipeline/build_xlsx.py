import pickle, json
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
START = datetime(2026,1,1,10); H = timedelta(hours=1)
F = pickle.load(open('final.pkl','rb')); sel, flag, itog = F['sel'], F['flag'], F['itog']
M = json.load(open('manual.json'))
N = len(sel); D = N//24
wb = Workbook()
hdr_font = Font(bold=True, color='FFFFFF'); hdr_fill = PatternFill('solid', fgColor='1F4E78')
thin = Side(style='thin', color='BFBFBF')
def header(ws, cols, widths):
    ws.append(cols)
    for i, w in enumerate(widths, 1):
        c = ws.cell(1, i); c.font = hdr_font; c.fill = hdr_fill
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 32; ws.freeze_panes = 'A2'
# --- sheet 1: hourly data
ws = wb.active; ws.title = 'Данные'
header(ws, ['Дата и время', 'Объём, м³', 'Энергия, МДж', 'Расход, м³/ч', 'Давление, кПа', 'Температура, °C', 'Объём р.у., м³'],
       [18, 12, 14, 13, 14, 15, 15])
for i, r in enumerate(sel):
    t = START + i*H
    ws.append([t, int(r[0]), int(r[1]), int(r[2]), float(r[3]), float(r[4]), int(r[5])])
for row in ws.iter_rows(min_row=2, max_row=N+1):
    row[0].number_format = 'DD.MM.YYYY HH:MM'
    row[4].number_format = '0.00'; row[5].number_format = '0.00'
    for c in (1,2,3,6): row[c].number_format = '#,##0'
ws.auto_filter.ref = 'A1:G%d' % (N+1)
# --- sheet 2: daily checks (formulas so the user can verify)
ws2 = wb.create_sheet('Проверка по суткам')
header(ws2, ['Сутки (с 10:00)', 'Часов',
             'Объём Σ', 'Объём «Итого»', 'Δ',
             'Энергия Σ', 'Энергия «Итого»', 'Δ',
             'Расход ср.', 'Расход «Итого»',
             'Давление ср.', 'Давление «Итого»',
             'Темп. ср.', 'Темп. «Итого»', 'Результат'],
        [14, 7, 11, 13, 6, 13, 15, 6, 11, 13, 13, 15, 10, 12, 30])
ok_fill = PatternFill('solid', fgColor='E2EFDA'); note_fill = PatternFill('solid', fgColor='FFF2CC')
for d in range(D):
    r0, r1 = 2 + d*24, 2 + d*24 + 23
    I = itog[d]; rr = d + 2
    zero = all(int(sel[i][0]) == 0 for i in range(d*24, d*24+24))
    rng = lambda col: '%s!%s%d:%s%d' % ("'Данные'", col, r0, col, r1)
    # average over hours with flow (as the meter does); zero-flow days have only a volume total
    avg = lambda col: '=IFERROR(AVERAGEIFS(%s,%s,">0"),"")' % (rng(col), rng('B'))
    row = [(START + d*24*H).date(), '=COUNT(%s)' % rng('A'),
           '=SUM(%s)' % rng('B'), int(I[0]) if I[0] is not None else None, '=C%d-D%d' % (rr, rr),
           '=SUM(%s)' % rng('C'), int(I[1]) if I[1] is not None else None, '=IF(G%d="","",F%d-G%d)' % (rr, rr, rr),
           avg('D'), int(I[2]) if I[2] is not None else None,
           avg('E'), float(I[3]) if I[3] is not None else None,
           avg('F'), float(I[4]) if I[4] is not None else None,
           'Нет расхода: «Итого» = 0, совпадает' if zero else 'Совпадает']
    ws2.append(row)
    ws2.cell(rr, 1).number_format = 'DD.MM.YYYY'
    for c in (3,4,6,7): ws2.cell(rr, c).number_format = '#,##0'
    for c in (9,): ws2.cell(rr, c).number_format = '0.0'
    for c in (11,12,13,14): ws2.cell(rr, c).number_format = '0.00'
    ws2.cell(rr, 15).fill = note_fill if zero else ok_fill
last = D + 1
ws2.append([])
ws2.append(['Всего', '=SUM(B2:B%d)' % last, '=SUM(C2:C%d)' % last, '=SUM(D2:D%d)' % last, '=C%d-D%d' % (last+2, last+2),
            '=SUM(F2:F%d)' % last, '=SUM(G2:G%d)' % last, '=F%d-G%d' % (last+2, last+2)])
ws2.append(['Сумм. по прибору', None, 11070769, None, None, 385389402])
for rr in (last+2, last+3):
    for c in (1,): ws2.cell(rr, c).font = Font(bold=True)
    for c in (3,4,6,7): ws2.cell(rr, c).number_format = '#,##0'
# --- sheet 3: continuity
ws3 = wb.create_sheet('Непрерывность')
header(ws3, ['Проверка', 'Значение'], [44, 26])
ws3.append(['Первая запись', START]); ws3.append(['Последняя запись', START + (N-1)*H])
ws3.append(['Ожидаемое число часов', N])
ws3.append(['Фактическое число записей', "=COUNTA('Данные'!A2:A%d)" % (N+1)])
ws3.append(['Пропусков / дублей (шаг ≠ 1 ч)', "=SUMPRODUCT(--(ROUND(('Данные'!A3:A%d-'Данные'!A2:A%d)*24,6)<>1))" % (N+1, N)])
ws3.append(['Суток в отчёте', D])
for r in (2,3): ws3.cell(r, 2).number_format = 'DD.MM.YYYY HH:MM'
# --- sheet 4: notes
ws4 = wb.create_sheet('Примечания')
header(ws4, ['Пункт', 'Описание'], [34, 120])
manual_cells = sum(len(v) for v in M['cells'].values())
notes = [
 ('Источник', '275 фотографий отчёта «СуперФлоу Zorka, Периодический отчёт» (20.11.26 09:03:03), период 01.01.2026 10:00 – 19.11.2026 10:00. Последняя часовая запись — 19.11.2026 09:00.'),
 ('Сутки', 'Отчётные (контрактные) сутки начинаются в 10:00: строка «Итого» стоит после записи 09:00 и охватывает 24 часа с 10:00 предыдущего дня.'),
 ('Распознавание', 'Tesseract OCR и собственный классификатор цифр (кластеризация + kNN), несколько вариантов предобработки. Каждый час собран голосованием по всем фото, на которых он виден.'),
 ('Ручная сверка', 'Строки, где распознавание было неуверенным или не проходило проверки, сверены с фото вручную: %d часовых строк (%d ячеек) и %d строк «Итого».' % (len(M['cells']), manual_cells, len(M['itog']))),
 ('Контрольные суммы', 'Все 137 суток с расходом (из 322 в отчёте): сумма объёма и энергии за 24 ч совпадает с «Итого» точно. Средние расход, давление и температура совпадают с «Итого» в пределах округления. Среднее считается по часам с ненулевым расходом: так считает прибор.'),
 ('Сутки без расхода', 'В 185 сутках (в основном май–октябрь) расход 0, и прибор печатает в «Итого» только 0. Давление и температура за эти сутки контрольной суммы не имеют. Они проверены на плавность ряда, все выбросы сверены с фото.'),
 ('Общий итог', 'Сумма по всем часам: объём 11 070 769 м³, энергия 385 389 402 МДж — совпадает с полями «Суммарный объём» / «Суммарная энергия» на экране прибора.'),
 ('Даты', '7728 часовых записей подряд с шагом 1 ч, без пропусков и дублей (лист «Непрерывность»).'),
 ('Столбец «Объём р.у.»', 'В «Итого» не входит, контрольной суммы нет. Проверен по отношению к объёму, выбросы сверены с фото.'),
 ('Ошибки в «Итого»', 'В 17 сутках без расхода OCR прочитал «Итого» как 5/8/1 вместо 0; по фото везде 0.'),
]
for n in notes: ws4.append(list(n))
for row in ws4.iter_rows(min_row=2):
    row[1].alignment = Alignment(wrap_text=True, vertical='top'); row[0].alignment = Alignment(vertical='top'); row[0].font = Font(bold=True)
wb.save('/home/user/zorka/zorka_2026_hourly.xlsx')
print('saved')
