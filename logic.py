"""Pure inventory policy: no web, database, or file dependencies."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import re
POLICY = 'classroom-v1'
ORDER_MULTIPLIER = Decimal('2')
MAX_INPUT = Decimal('1000000')
class ValidationError(ValueError): pass

def number(value, name, integer=False):
    if value is None or isinstance(value, bool) or str(value).strip() == '':
        raise ValidationError(f'{name} is required and must be numeric.')
    try: n = Decimal(str(value))
    except InvalidOperation: raise ValidationError(f'{name} must be numeric.')
    if not n.is_finite() or n < 0 or n > MAX_INPUT:
        raise ValidationError(f'{name} must be finite and between 0 and 1,000,000.')
    if integer and n != n.to_integral_value():
        raise ValidationError(f'{name} must be a whole item count.')
    return n

def calculate(row):
    if not isinstance(row, dict): raise ValidationError('Each item must be an object.')
    if not isinstance(row.get('sku'),str) or not isinstance(row.get('item'),str):
        raise ValidationError('SKU and item name are required text fields.')
    sku = row['sku'].strip().upper()
    item = str(row.get('item','')).strip()
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9_-]{0,31}', sku):
        raise ValidationError('SKU must contain 1–32 letters, digits, hyphens or underscores.')
    if not item or len(item)>120: raise ValidationError('Item name must contain 1–120 characters.')
    if row.get('unit') != 'each': raise ValidationError('Unsupported unit: use each. No pack conversion is implied.')
    if row.get('lead_unit') != 'weeks': raise ValidationError('Unsupported lead-time unit: use weeks.')
    stock=number(row.get('on_hand'),'On hand',True)
    use=number(row.get('weekly_use'),'Weekly use')
    lead=number(row.get('lead_time'),'Lead time')
    safety=number(row.get('safety_stock'),'Safety stock',True)
    demand=use*lead
    point=demand+safety
    reorder=stock<=point
    exact=ORDER_MULTIPLIER*point-stock if reorder else Decimal(0)
    qty=int(exact.to_integral_value(rounding=ROUND_CEILING))
    return dict(sku=sku,item=item,on_hand=int(stock),weekly_use=float(use),lead_time=float(lead),
                safety_stock=int(safety),unit='each',lead_unit='weeks',demand=float(demand),
                reorder_point=float(point),reorder='YES' if reorder else 'NO',order_qty=qty,
                exact_order_qty=float(exact),policy=POLICY)

def review(rows):
    if not isinstance(rows,list) or not 1<=len(rows)<=100:
        raise ValidationError('A review requires 1–100 items.')
    results=[]; seen=set()
    for i,row in enumerate(rows,1):
        try: result=calculate(row)
        except ValidationError as e: raise ValidationError(f'Item {i}: {e}') from e
        if result['sku'] in seen: raise ValidationError(f"Duplicate SKU: {result['sku']}. Nothing was saved.")
        seen.add(result['sku']);results.append(result)
    return results
