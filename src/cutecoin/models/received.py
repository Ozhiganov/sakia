'''
Created on 5 févr. 2014

@author: inso
'''

import logging
from PyQt5.QtCore import QAbstractListModel, Qt


class ReceivedListModel(QAbstractListModel):

    '''
    A Qt abstract item model to display communities in a tree
    '''

    def __init__(self, account, community, parent=None):
        '''
        Constructor
        '''
        super(ReceivedListModel, self).__init__(parent)
        self.account = account
        self.community = community

    def rowCount(self, parent):
        return len(self.account.transactions_received(self.community))

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = index.row()
            transactions = self.account.transactions_received(self.community)
            value = transactions[row].get_receiver_text()
            return value

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled