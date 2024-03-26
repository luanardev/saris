from django_tables2.columns import CheckBoxColumn


class SelectAllCheckBoxColumn(CheckBoxColumn):
    def __init__(self, attrs=None, checked=None, **extra):
        attrs = {"th__input": {"name": "selectall", "class": "selectall"}}
        super().__init__(attrs, checked, **extra)


class BulkSelectionMixin(object):
    has_bulk_action=True
    edit_selected_url=None
    delete_selected_url=None
    