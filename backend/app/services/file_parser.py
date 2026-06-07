import pandas as pd
import io
import re
import pdfplumber
from datetime import datetime


def parse_csv(file):
    try:
        content = file.read()
        try:
            text = content.decode('utf-8-sig')
        except:
            text = content.decode('latin-1')
        df = pd.read_csv(io.StringIO(text))
        df.columns = df.columns.str.strip().str.lower().str.replace('\ufeff', '').str.replace('?', '')
        required = {'date', 'description', 'amount'}
        if not required.issubset(df.columns):
            return None, f"CSV deve ter as colunas: {', '.join(required)}. Encontradas: {', '.join(df.columns)}"
        expenses = []
        errors = []
        for index, row in df.iterrows():
            try:
                expense = {
                    'date': str(pd.to_datetime(row['date']).date()),
                    'description': str(row['description']).strip(),
                    'amount': float(row['amount']),
                    'category': str(row.get('category', 'Outros')).strip()
                }
                expenses.append(expense)
            except Exception as e:
                errors.append(f"Linha {index + 2}: {str(e)}")
        return expenses, errors
    except Exception as e:
        return None, str(e)


def _is_valid_amount(text):
    return bool(re.match(r'^\d{1,3}(?:\.\d{3})*,\d{2}$', text.strip()))


def _to_float(text):
    return float(text.strip().replace('.', '').replace(',', '.'))


def parse_pdf_bradesco(file, year=None):
    expenses = []

    IGNORE_PATTERNS = [
        r'PAGTO', r'PAGAMENTO', r'Historico', r'Lancamentos',
    ]

    try:
        with pdfplumber.open(file) as pdf:
            first_text = pdf.pages[0].extract_text() or ''

            # Tenta encontrar vencimento após a palavra "Vencimento"
            venc_match = re.search(r'[Vv]encimento[^\d]*(\d{2})/(\d{2})/(\d{4})', first_text)

            # Se não achou, tenta pegar a data após um valor R$
            if not venc_match:
                venc_match = re.search(r'R\$\s*[\d.,]+\s*(\d{2})/(\d{2})/(\d{4})', first_text)

            if venc_match:
                venc_day = int(venc_match.group(1))
                venc_month = int(venc_match.group(2))
                venc_year = int(venc_match.group(3))
            else:
                venc_day = 1
                venc_month = datetime.now().month
                venc_year = year or datetime.now().year

            date_full = f"{venc_year}-{venc_month:02d}-{venc_day:02d}"

            for page in pdf.pages:
                words = page.extract_words()
                if not words:
                    continue

                date_col   = [w for w in words if w['x0'] < 60]
                desc_col   = [w for w in words if 60 <= w['x0'] < 200]
                amount_col = [w for w in words if 318 <= w['x0'] <= 342]

                amounts_by_y = {}
                for w in amount_col:
                    if _is_valid_amount(w['text']) and not w['text'].endswith('-'):
                        y = round(w['top'])
                        amounts_by_y[y] = w['text']

                for dw in date_col:
                    date_match = re.match(r'^(\d{2})/(\d{2})$', dw['text'])
                    if not date_match:
                        continue

                    date_y = round(dw['top'])

                    desc_words = [
                        w['text'] for w in desc_col
                        if abs(round(w['top']) - date_y) <= 4
                    ]
                    description = ' '.join(desc_words).strip()
                    description = re.sub(r'\s*\S{0,3}\d{2}/\d{2}\s*$', '', description).strip()

                    if not description:
                        continue

                    should_ignore = any(
                        re.search(p, description, re.IGNORECASE)
                        for p in IGNORE_PATTERNS
                    )
                    if should_ignore:
                        continue

                    amount = None
                    for search_y in range(date_y - 2, date_y + 16):
                        if search_y in amounts_by_y:
                            amount = _to_float(amounts_by_y[search_y])
                            break

                    if amount is None or amount <= 0 or amount > 1500:
                        continue

                    expenses.append({
                        'date': date_full,
                        'description': description,
                        'amount': amount,
                        'category': 'Outros'
                    })

        seen = set()
        unique = []
        for e in expenses:
            key = (e['date'], e['description'], e['amount'])
            if key not in seen:
                seen.add(key)
                unique.append(e)

        return expenses, []

    except Exception as e:
        return None, str(e)
