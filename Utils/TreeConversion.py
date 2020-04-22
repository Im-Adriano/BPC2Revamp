from PySide2.QtGui import QStandardItemModel
from PySide2.QtWidgets import QApplication, QTreeView, QTreeWidgetItem


def fill_model_from_json(parent, d):
    if isinstance(d, dict):
        for k, v in d.items():
            child = QTreeWidgetItem()
            child.setText(0, str(k))
            parent.addChild(child)
            fill_model_from_json(child, v)
    elif isinstance(d, list):
        for v in d:
            fill_model_from_json(parent, v)
    else:
        item = QTreeWidgetItem()
        item.setText(0, str(d))
        parent.addChild(item)


def fill_dict_from_model(parent_index, d, m):
    v = {}
    for i in range(m.rowCount(parent_index)):
        ix = m.index(i, 0, parent_index)
        fill_dict_from_model(ix, v, m)
    d[parent_index.data()] = v


def model_to_dict(m):
    d = dict()
    for i in range(m.rowCount()):
        ix = m.index(i, 0)
        fill_dict_from_model(ix, d, m)
    return d


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    tree = QTreeView()
    model = QStandardItemModel()
    data = {"A": {"B": {"H": {}, "I": {"M": {}, "N": {}}}, "D": {}, "E": {}, "F": {}, "G": {"L": {}},
                  "C": {"J": {}, "K": {}}}}
    fill_model_from_json(model.invisibleRootItem(), data)
    tree.setModel(model)
    tree.expandAll()
    tree.resize(360, 480)
    tree.show()
    dic = model_to_dict(model)
    assert (dic == data)
    print(dic)
    sys.exit(app.exec_())
