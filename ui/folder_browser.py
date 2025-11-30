from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
import os

class FolderBrowser(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Музыкальные папки")
        self.setColumnCount(2)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setColumnHidden(1, True)
        
        self.audio_files = {}
    
    def load_folders(self, audio_files_dict: dict):
        self.audio_files = audio_files_dict
        self.clear()
        
        for folder_path, files in audio_files_dict.items():
            folder_name = os.path.basename(folder_path)
            if not folder_name:
                folder_name = folder_path
                
            folder_item = QTreeWidgetItem([folder_name, folder_path])
            folder_item.setData(0, Qt.ItemDataRole.UserRole, files)
            
            for file_path in files:
                file_name = os.path.basename(file_path)
                file_item = QTreeWidgetItem([file_name, file_path])
                file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                folder_item.addChild(file_item)
            
            self.addTopLevelItem(folder_item)
        
        self.expandAll()