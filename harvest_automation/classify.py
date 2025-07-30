
def is_billable(
    title_lower: str,
    bill_kw: tuple[str, ...],
    nonbill_kw: tuple[str, ...],
    default_billable: bool,
) -> bool:
    if any(nk in title_lower for nk in nonbill_kw):
        return False
    if any(bk in title_lower for bk in bill_kw):
        return True
    return default_billable
