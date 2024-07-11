# uncompyle6 version 3.9.1
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.11.9 (main, Apr  2 2024, 08:25:04) [Clang 15.0.0 (clang-1500.3.9.4)]
# Embedded file name: Prism_Populator.py
import wx
import wx.lib.agw.genericmessagedialog as GMD
from lxml import etree as ET
import pandas, re
from collections import OrderedDict
import os
from xlsxwriter.utility import xl_rowcol_to_cell
import numpy, sys, traceback
__version__ = "1.0.2"

def exception_handler(exc_type, exc_value, exc_traceback):
    """Handle unhandled exceptions so the user gets a dialog box with the error."""
    message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(message)
    msg_dlg = wx.MessageDialog(None, message, "Unhandled Exception", wx.OK | wx.ICON_EXCLAMATION)
    msg_dlg.ShowModal()
    msg_dlg.Destroy()
    exit(1)


sys.excepthook = exception_handler

class Prism_Populator_GUI(wx.Frame):

    def __init__(self, parent, title, *args, **kwargs):
        (super(Prism_Populator_GUI, self).__init__)(parent, *args, title=title, **kwargs)
        self.InitUI()
        self.Fit()
        self.Centre()
        self.Show()

    def InitUI(self):
        self.groups = OrderedDict()
        self.input_data_file_okay = False
        self.input_prism_file_okay = False
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        about_item = fileMenu.Append(100, "&About   \tCtrl+A", "Information about the program")
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        fileMenu.AppendSeparator()
        quit_item = wx.MenuItem(fileMenu, 101, "Quit", "Quit Application")
        fileMenu.Append(quit_item)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        menubar.Append(fileMenu, "&File")
        self.SetMenuBar(menubar)
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        radio_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.error_radio_box = wx.RadioBox(panel, label="Error Calculation", choices=["SEM", "STD"], pos=(0,
                                                                                                          0), majorDimension=1, style=(wx.RA_SPECIFY_ROWS))
        self.error_radio_box.SetSelection(0)
        self.current_error_type = "SEM"
        self.error_radio_box.Bind(wx.EVT_RADIOBOX, self.onErrorRadioBox)
        radio_box_sizer.Add((self.error_radio_box), flag=(wx.ALIGN_LEFT | wx.LEFT), border=10)
        vbox.Add(radio_box_sizer)
        data_file_label = wx.StaticText(panel, label="Data File:")
        self.data_file_st = wx.StaticText(panel)
        self.data_file_st.SetMinSize((450, 20))
        vbox.Add(data_file_label, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.TOP), border=10)
        vbox.Add((self.data_file_st), flag=(wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT), border=10)
        open_data_button = wx.Button(panel, label="Open Data File")
        open_data_button.Bind(wx.EVT_BUTTON, self.OnDataOpen)
        vbox.Add(open_data_button, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM), border=10)
        prism_file_label = wx.StaticText(panel, label="Prism File:")
        self.prism_file_st = wx.StaticText(panel)
        self.prism_file_st.SetMinSize((450, 20))
        vbox.Add(prism_file_label, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.TOP), border=10)
        vbox.Add((self.prism_file_st), flag=(wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT), border=10)
        open_prism_button = wx.Button(panel, label="Open Prism File")
        open_prism_button.Bind(wx.EVT_BUTTON, self.OnPrismOpen)
        vbox.Add(open_prism_button, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM), border=10)
        line = wx.StaticLine(panel)
        vbox.Add(line, flag=(wx.EXPAND | wx.LEFT | wx.RIGHT), border=10)
        sizer = wx.FlexGridSizer(2, 3, 0, 10)
        st1 = wx.StaticText(panel, label="Groups")
        st2 = wx.StaticText(panel, label="Samples")
        st3 = wx.StaticText(panel, label="Normalizing Compounds")
        sizer.Add(st1)
        sizer.Add(st2)
        sizer.Add(st3)
        self.samples_listbox = wx.ListBox(panel, style=(wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.LB_SORT))
        self.samples_listbox.SetMinSize((333, 200))
        self.groups_listbox = wx.ListBox(panel, style=(wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB))
        self.groups_listbox.SetMinSize((333, 200))
        self.groups_listbox.Bind(wx.EVT_LISTBOX, self.onListBox)
        self.compounds_listbox = wx.CheckListBox(panel, style=(wx.LB_SORT))
        self.compounds_listbox.SetMinSize((333, 200))
        sizer.Add((self.groups_listbox), flag=(wx.EXPAND))
        sizer.Add((self.samples_listbox), flag=(wx.EXPAND))
        sizer.Add((self.compounds_listbox), flag=(wx.EXPAND))
        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableCol(2, 1)
        sizer.AddGrowableRow(1, 1)
        vbox.Add(sizer, proportion=1, flag=(wx.EXPAND | wx.ALL), border=10)
        # vbox.Add(sizer, proportion=1, flag=wx.ALL, border=10)
        # vbox.Add(sizer, proportion=1, flag=(wx.EXPAND | wx.ALL | wx.ALIGN_CENTER), border=10)
        group_buttons_header = wx.StaticText(panel, label="Group Management:")
        vbox.Add(group_buttons_header, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.TOP), border=10)
        add_group_button = wx.Button(panel, label="Add Group")
        add_group_button.Bind(wx.EVT_BUTTON, self.Add_Group)
        delete_group_button = wx.Button(panel, label="Delete Group")
        delete_group_button.Bind(wx.EVT_BUTTON, self.Delete_Group)
        move_group_up_button = wx.Button(panel, label="Move Group Up")
        move_group_up_button.Bind(wx.EVT_BUTTON, self.Move_Group_Up_or_Down)
        move_group_down_button = wx.Button(panel, label="Move Group Down")
        move_group_down_button.Bind(wx.EVT_BUTTON, self.Move_Group_Up_or_Down)
        add_sample_button = wx.Button(panel, label="Add Sample")
        add_sample_button.Bind(wx.EVT_BUTTON, self.Add_Sample)
        delete_sample_button = wx.Button(panel, label="Delete Sample")
        delete_sample_button.Bind(wx.EVT_BUTTON, self.Delete_Sample)
        group_buttons_hbox = wx.BoxSizer(wx.HORIZONTAL)
        group_buttons_hbox.Add(add_group_button, flag=(wx.RIGHT | wx.TOP | wx.BOTTOM), border=5)
        group_buttons_hbox.Add(delete_group_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(move_group_up_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(move_group_down_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(add_sample_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(delete_sample_button, flag=(wx.ALL), border=5)
        vbox.Add(group_buttons_hbox, flag=(wx.ALIGN_LEFT | wx.ALL), border=10)
        plot_buttons_header = wx.StaticText(panel, label="Populate Data:")
        vbox.Add(plot_buttons_header, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.TOP), border=10)
        run_button = wx.Button(panel, label="Create Prism File")
        run_button.Bind(wx.EVT_BUTTON, self.Create_Prism_File)
        create_excel_plots_button = wx.Button(panel, label="Create Excel Plots")
        create_excel_plots_button.Bind(wx.EVT_BUTTON, self.Save_Plot_Data)
        save_plot_data_button = wx.Button(panel, label="Save Plot Data")
        save_plot_data_button.Bind(wx.EVT_BUTTON, self.Save_Plot_Data)
        plot_buttons_hbox = wx.BoxSizer(wx.HORIZONTAL)
        plot_buttons_hbox.Add(run_button, flag=(wx.RIGHT | wx.TOP | wx.BOTTOM), border=5)
        plot_buttons_hbox.Add(create_excel_plots_button, flag=(wx.ALL), border=5)
        plot_buttons_hbox.Add(save_plot_data_button, flag=(wx.ALL), border=5)
        vbox.Add(plot_buttons_hbox, flag=(wx.ALIGN_LEFT | wx.ALL), border=10)
        panel.SetSizer(vbox)
        panel.Fit()

    def OnAbout(self, event):
        message = "Author: Travis Thompson \n\nCreation Date: April 2019 \nVersion Number: " + __version__
        dlg = GMD.GenericMessageDialog(None, message, "About", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnQuit(self, e):
        self.Close()

    def onErrorRadioBox(self, event):
        radio_box = event.GetEventObject()
        self.current_error_type = radio_box.GetStringSelection()

    def onListBox(self, event):
        """"""
        groups_listbox = event.GetEventObject()
        selected_group = groups_listbox.GetStringSelection()
        self.samples_listbox.Set(self.groups[selected_group])

    def Update_Group_List(self):
        """"""
        self.groups_listbox.Set(list(self.groups.keys()))

    def Add_Group(self, event):
        """"""
        if self.input_data_file_okay == False:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        initial_groups_length = len(self.groups)
        group_name = ""
        while group_name == "":
            dlg = wx.TextEntryDialog(None, "Enter the group name:", "Group Name")
            if dlg.ShowModal() == wx.ID_OK:
                group_name = dlg.GetValue()
                if group_name == "":
                    message = "Please enter a valid group name."
                    msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return

        selections = []
        while len(selections) == 0:
            sample_names = list(self.sample_names)
            dlg = wx.MultiChoiceDialog(None, "Select the samples in group " + group_name + ":", 'Samples in Group "' + group_name + '"', sample_names)
            if dlg.ShowModal() == wx.ID_OK:
                selections = dlg.GetSelections()
                if len(selections) != 0:
                    self.groups[group_name] = [sample_names[x] for x in selections]
                else:
                    message = "Please select at least one sample for the group."
                    msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return

        if len(self.groups) > initial_groups_length:
            self.Update_Group_List()

    def Delete_Group(self, event):
        """"""
        if self.input_data_file_okay == False:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        else:
            if len(self.groups) == 0:
                message = "There are no groups to delete."
                msg_dlg = wx.MessageDialog(None, message, "No Groups To Delete", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
                return
            selected_group = self.groups_listbox.GetStringSelection()
            selected_group_index = self.groups_listbox.GetSelection()
            if selected_group != wx.NOT_FOUND:
                self.groups.pop(selected_group)
                self.Update_Group_List()
                if len(self.groups) > 0:
                    if selected_group_index < len(self.groups):
                        self.groups_listbox.SetSelection(selected_group_index)
                    else:
                        self.groups_listbox.SetSelection(selected_group_index - 1)
                    selected_group = self.groups_listbox.GetStringSelection()
                    self.samples_listbox.Set(self.groups[selected_group])
                else:
                    self.samples_listbox.Clear()
            else:
                message = "No group selected."
                msg_dlg = wx.MessageDialog(None, message, "No Group Selected", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()

    def Move_Group_Up_or_Down(self, event):
        button = event.GetEventObject()
        if self.input_data_file_okay == False:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        else:
            if len(self.groups) == 0:
                message = "There are no groups to move."
                msg_dlg = wx.MessageDialog(None, message, "No Groups To Move", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
                return
            selected_group = self.groups_listbox.GetStringSelection()
            selected_index = self.groups_listbox.GetSelection()
            if selected_group != wx.NOT_FOUND:
                index = list(self.groups.keys())
                selected_group_index = index.index(selected_group)
                groups = list(self.groups.items())
                if button.GetLabel() == "Move Group Up":
                    swap_temp = groups[selected_group_index - 1]
                    groups[selected_group_index - 1] = groups[selected_group_index]
                elif selected_group_index + 1 >= len(self.groups):
                    swap_temp = groups[0]
                    groups[0] = groups[selected_group_index]
                else:
                    swap_temp = groups[selected_group_index + 1]
                    groups[selected_group_index + 1] = groups[selected_group_index]
                groups[selected_group_index] = swap_temp
                self.groups = OrderedDict()
                for key, value in groups:
                    self.groups[key] = value

                self.Update_Group_List()
                if button.GetLabel() == "Move Group Up":
                    if selected_index > 0:
                        self.groups_listbox.SetSelection(selected_index - 1)
                    else:
                        self.groups_listbox.SetSelection(len(self.groups) - 1)
                elif selected_index + 1 >= len(self.groups):
                    self.groups_listbox.SetSelection(0)
                else:
                    self.groups_listbox.SetSelection(selected_index + 1)
            else:
                message = "No group selected."
                msg_dlg = wx.MessageDialog(None, message, "No Group Selected", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()

    def Add_Sample(self, event):
        """"""
        if self.input_data_file_okay == False:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        selected_group = self.groups_listbox.GetStringSelection()
        if selected_group != "":
            samples_to_display = list(self.sample_names)
            for sample_name in self.groups[selected_group]:
                index_to_delete = samples_to_display.index(sample_name)
                del samples_to_display[index_to_delete]

            if len(samples_to_display) > 0:
                dlg = wx.MultiChoiceDialog(None, "Select the samples to add to group " + selected_group + ":", 'Add Samples To Group "' + selected_group + '"', samples_to_display)
                if dlg.ShowModal() == wx.ID_OK:
                    selections = dlg.GetSelections()
                    if len(selections) != 0:
                        self.groups[selected_group] = self.groups[selected_group] + [samples_to_display[x] for x in selections]
                        self.groups[selected_group] = [sample for sample in self.sample_names if sample in self.groups[selected_group]]
                        self.samples_listbox.Set(self.groups[selected_group])
                dlg.Destroy()
            else:
                message = "Group contains all samples."
                msg_dlg = wx.MessageDialog(None, message, "No More Samples", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
        else:
            message = "No group selected."
            msg_dlg = wx.MessageDialog(None, message, "No Group Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()

    def Delete_Sample(self, event):
        """"""
        if self.input_data_file_okay == False:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        else:
            selected_group = self.groups_listbox.GetStringSelection()
            if selected_group != "":
                sample_to_delete = self.samples_listbox.GetStringSelection()
                index_of_selection = self.samples_listbox.GetSelection()
                if sample_to_delete != wx.NOT_FOUND and sample_to_delete != "":
                    if len(self.groups[selected_group]) == 1:
                        message = "Groups must contain at least one sample."
                        msg_dlg = wx.MessageDialog(None, message, "Not Enough Samples", wx.OK | wx.ICON_EXCLAMATION)
                        msg_dlg.ShowModal()
                        msg_dlg.Destroy()
                    else:
                        index_to_delete = self.groups[selected_group].index(sample_to_delete)
                        del self.groups[selected_group][index_to_delete]
                        self.samples_listbox.Set(self.groups[selected_group])
                        if index_of_selection < len(self.groups[selected_group]):
                            self.samples_listbox.SetSelection(index_of_selection)
                        else:
                            self.samples_listbox.SetSelection(index_of_selection - 1)
                else:
                    message = "No sample selected."
                    msg_dlg = wx.MessageDialog(None, message, "No Sample Selected", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
            else:
                message = "No group selected."
                msg_dlg = wx.MessageDialog(None, message, "No Group Selected", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()

    def OnDataOpen(self, e):
        previous_file_status = self.input_data_file_okay
        self.input_data_file_okay = True
        data_sheet = 0
        dlg = wx.FileDialog(self, message="Select Excel or csv File", style=(wx.FD_OPEN))
        if dlg.ShowModal() == wx.ID_OK:
            self.data_file_path = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            if previous_file_status:
                self.input_data_file_okay = True
                return
            else:
                self.input_data_file_okay = False
                return
            if not re.match(".*\\.xlsx|.*\\.xlsm|.*\\.xls|.*\\.csv", self.data_file_path):
                message = "The selected file is not the right type."
                msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
                self.input_data_file_okay = False
                return
            if re.match(".*\\.xlsx|.*\\.xlsm|.*\\.xls", self.data_file_path):
                workbook = pandas.ExcelFile(self.data_file_path)
                sheets = workbook.sheet_names
                sheets.sort()
                if len(sheets) == 0:
                    message = "The sheet names of the selected file cannot be detected. \nTry saving in a different format."
                    msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
                    self.input_data_file_okay = False
                    return
                if len(sheets) > 1:
                    data_sheet = "Sheet1"
                    if data_sheet not in sheets:
                        dlg = wx.SingleChoiceDialog(None, "Select the sheet with data:", "Sheets", sheets)
                        if dlg.ShowModal() == wx.ID_OK:
                            selection = dlg.GetSelection()
                            data_sheet = sheets[selection]
                            dlg.Destroy()
                    else:
                        dlg.Destroy()
                        self.input_data_file_okay = False
                        return
                self.data_df = pandas.read_excel(workbook, sheet_name=data_sheet, index_col=0)
                self.data_df.drop(index=(self.data_df.index[0]), inplace=True)
                self.data_df = self.data_df.transpose()
            else:
                self.data_df = pandas.read_csv((self.data_file_path), index_col=0)
                self.data_df.drop(index=(self.data_df.index[0]), inplace=True)
                self.data_df = self.data_df.transpose()
        if len(self.data_df.columns) > len(self.data_df.columns.unique()):
            message = "The sample names are not unique."
            msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            self.input_data_file_okay = False
            return
        if len(self.data_df.index) > len(self.data_df.index.unique()):
            message = "The compound names are not unique."
            msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            self.input_data_file_okay = False
            return
        self.sample_names = list(self.data_df.columns)
        self.data_file_st.SetLabel(self.data_file_path)
        self.data_directory_path = os.path.split(self.data_file_path)[0]
        self.groups = OrderedDict()
        self.groups_listbox.Clear()
        self.samples_listbox.Clear()
        self.compounds_listbox.Clear()
        self.compounds_listbox.Set(list(self.data_df.index))

    def Save_Plot_Data(self, event):
        """"""
        group_dataframe = pandas.DataFrame(index=(self.sample_names), columns=(self.groups.keys()))
        for i in range(len(group_dataframe.columns)):
            for j in range(len(group_dataframe.index)):
                if group_dataframe.index[j] in self.groups[group_dataframe.columns[i]]:
                    group_dataframe.iloc[(j, i)] = "X"
                else:
                    group_dataframe.iloc[(j, i)] = ""

        create_plots = False
        if event.GetEventObject().GetLabel() == "Create Excel Plots":
            create_plots = True
        if self.input_data_file_okay == False:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No Excel File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        if len(self.groups) == 0:
            message = "Please create some groups to include their information in the sheet."
            msg_dlg = wx.MessageDialog(None, message, "No Groups", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        tables_to_print = []
        table_titles = [
         "Average Normalized Intensity of Groups",
         self.current_error_type + " of Normalized Intensity of Groups"]
        self.Print_Tables_To_Excel(create_plots=create_plots, group_dataframe=group_dataframe, sheet_name="Data_Plots",
          tables_to_print=tables_to_print,
          table_titles=table_titles,
          rows_between_title_and_data=1,
          rows_between_dfs=3,
          rows_between_graphs_and_data=6,
          data_type="",
          y_axis_label="Normalized Intensity",
          dataframe_to_graph=(self.data_df),
          average_table_title="Average Normalized Intensity of Groups")
        self.writer.save()

    def Write_DF_To_Excel(self, title, sheet_name, rows_between_title_and_data, dataframe, startrow=0, startcol=0, columns=None):
        table_title = pandas.DataFrame(index=[title])
        table_title.to_excel((self.writer), columns=columns, sheet_name=sheet_name, startrow=startrow, startcol=startcol)
        row = startrow + rows_between_title_and_data
        dataframe.to_excel((self.writer), sheet_name=sheet_name, startrow=row, startcol=startcol)

    def Insert_Graphs_To_Excel(self, insert_row, group_average, group_half_error, average_startrow, error_startrow, y_axis_label, worksheet, workbook, negative_error_row, sheet_name, data_type=None, insert_col=0, charts_to_a_row=4):
        insert_row = insert_row
        insert_col = insert_col
        number_of_charts_to_a_row = charts_to_a_row
        loop_count = 0
        overlap = -100
        compound_column_name = "Compound"
        if type(group_average.columns) == pandas.core.indexes.multi.MultiIndex:
            data_is_MultiIndex = True
        else:
            data_is_MultiIndex = False
        if data_is_MultiIndex:
            compounds = group_average.columns.levels[group_average.columns.names.index(compound_column_name)]
        else:
            compounds = group_average.columns
        for compound in compounds:
            chart = workbook.add_chart({"type": "column"})
            for group_name in group_average.index:
                if data_is_MultiIndex:
                    absolute_average_row = group_average.index.get_loc(group_name) + average_startrow + len(group_average.columns.names) + 1
                    absolute_error_row = group_half_error.index.get_loc(group_name) + error_startrow + len(group_half_error.columns.names) + 1
                    int_or_slice = group_average.columns.get_level_values(group_average.columns.names.index(compound_column_name)).get_loc(compound)
                    categorie_row = average_startrow + group_average.columns.names.index("Isomers_String")
                else:
                    absolute_average_row = group_average.index.get_loc(group_name) + average_startrow + len(group_average.columns.names)
                    absolute_error_row = group_half_error.index.get_loc(group_name) + error_startrow + len(group_half_error.columns.names)
                    int_or_slice = group_average.columns.get_loc(compound)
                    categorie_row = average_startrow
                if type(int_or_slice) == slice:
                    start_col = 1 + int_or_slice.start
                    stop_col = int_or_slice.stop
                elif type(int_or_slice) == numpy.ndarray:
                    int_or_slice = pandas.Series(int_or_slice)
                    start_col = int_or_slice[int_or_slice].index[0] + 1
                    stop_col = int_or_slice[int_or_slice].index[-1] + 1
                else:
                    start_col = 1 + int_or_slice
                    stop_col = 1 + int_or_slice
                pos_start_cell = xl_rowcol_to_cell(absolute_error_row, start_col, row_abs=True, col_abs=True)
                pos_stop_cell = xl_rowcol_to_cell(absolute_error_row, stop_col, row_abs=True, col_abs=True)
                neg_start_cell = xl_rowcol_to_cell(negative_error_row, start_col, row_abs=True, col_abs=True)
                neg_stop_cell = xl_rowcol_to_cell(negative_error_row, stop_col, row_abs=True, col_abs=True)
                chart.add_series({'values':[sheet_name, absolute_average_row, start_col, absolute_average_row, 
                  stop_col],  'categories':[
                  sheet_name, categorie_row, 
                  start_col, 
                  categorie_row, stop_col], 
                 'name':[
                  sheet_name, absolute_average_row, 0], 
                 'border':{'color':"black", 
                  'width':1}, 
                 'overlap':overlap, 
                 'y_error_bars':{'type':"custom", 
                  'plus_values':("=" + sheet_name + "!" + pos_start_cell + ":") + pos_stop_cell, 
                  'minus_values':("=" + sheet_name + "!" + neg_start_cell + ":") + neg_stop_cell}})

            chart.set_y_axis({'name':y_axis_label,  'name_font':{'name':"Arial", 
              'size':20,  'bold':True}, 
             'num_font':{'name':"Arial", 
              'size':18,  'bold':True}, 
             'major_gridlines':{"visible": False}})
            chart.set_x_axis({"num_font": {'name':"Arial",  'size':18,  'bold':True}})
            chart.set_title({'name':compound,  'name_font':{'name':"Arial", 
              'size':28,  'bold':True}, 
             'overlay':True})
            chart.set_chartarea({"border": {"none": True}})
            chart.set_legend({'font':{'name':"Arial",  'size':14,  'bold':True},  'position':"overlay_right"})
            worksheet.insert_chart(insert_row, insert_col, chart)
            loop_count += 1
            if loop_count % number_of_charts_to_a_row == 0:
                insert_col = 0
                insert_row += 15
            else:
                insert_col += 8

    def Print_Tables_To_Excel(self, create_plots, group_dataframe, sheet_name, tables_to_print, table_titles, rows_between_title_and_data, rows_between_dfs, rows_between_graphs_and_data, data_type, y_axis_label, dataframe_to_graph, average_table_title):
        normalizing_compounds = list(self.compounds_listbox.GetCheckedStrings())
        if len(normalizing_compounds) > 0:
            normalized_data_df = self.data_df.copy(deep=True)
            normalized_compound_data = self.data_df.loc[normalizing_compounds]
            for normalizing_compound in normalizing_compounds:
                for sample in self.data_df.columns:
                    normalized_data_df.loc[:, sample] = normalized_data_df.loc[:, sample] / normalized_compound_data.loc[(normalizing_compound, sample)]

        else:
            normalized_data_df = self.data_df
        group_mean_data_df = pandas.DataFrame()
        group_error_data_df = pandas.DataFrame()
        for group_name, samples in self.groups.items():
            group_mean_data_df.loc[:, group_name] = normalized_data_df.loc[:, samples].mean(axis=1)
            if self.current_error_type == "STD":
                group_error_data_df.loc[:, group_name] = normalized_data_df.loc[:, samples].std(axis=1)
            else:
                group_error_data_df.loc[:, group_name] = normalized_data_df.loc[:, samples].sem(axis=1)

        group_mean_data_df = group_mean_data_df.transpose()
        group_error_data_df = group_error_data_df.transpose()
        if type(group_mean_data_df.columns) == pandas.core.indexes.multi.MultiIndex:
            group_mean_data_df.index.name = "GroupID"
            group_error_data_df.index.name = "GroupID"
        else:
            tables_to_print.append(group_mean_data_df)
            tables_to_print.append(group_error_data_df)
            dlg = wx.FileDialog(self,
              message="Save file as ...", defaultDir=(self.data_directory_path),
              defaultFile="",
              style=(wx.FD_SAVE))
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
        if not re.match(".*\\.xlsx", path):
            path = path + ".xlsx"
        else:
            self.writer = pandas.ExcelWriter(path, engine="xlsxwriter")
            row = 0
            for i in range(len(tables_to_print)):
                self.Write_DF_To_Excel((table_titles[i]), startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data,
                  dataframe=(tables_to_print[i]))
                if table_titles[i] == average_table_title:
                    average_data_start_row = row + rows_between_title_and_data
                row = row + len(tables_to_print[i]) + rows_between_title_and_data + rows_between_dfs

            self.Write_DF_To_Excel("Normalized Intensity", startrow=0, sheet_name="Normalized_Data", rows_between_title_and_data=rows_between_title_and_data,
              dataframe=(normalized_data_df.transpose()))
            if create_plots:
                group_half_error = group_error_data_df / 2
                group_half_error.loc["negative_error"] = 0
                self.Write_DF_To_Excel(("Half " + self.current_error_type + " for Plots"), startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data,
                  dataframe=group_half_error)
                row = row + rows_between_title_and_data
                half_error_start_row = row
                negative_error_row = row + group_half_error.index.get_loc("negative_error") + 1 + len(group_half_error.columns.names)
                row = row + len(group_half_error) + rows_between_dfs
            self.Write_DF_To_Excel("Samples in Each Group", startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data,
              dataframe=group_dataframe)
            if len(normalizing_compounds) > 0:
                row = row + len(group_dataframe) + rows_between_title_and_data + rows_between_dfs
            else:
                row = row + len(group_dataframe) + rows_between_graphs_and_data + rows_between_title_and_data
        if len(normalizing_compounds) > 0:
            normalizing_compounds_df = pandas.DataFrame(index=normalizing_compounds)
            self.Write_DF_To_Excel("Normalizing Compounds", startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data,
              dataframe=normalizing_compounds_df)
            row = row + len(normalizing_compounds_df) + rows_between_graphs_and_data + rows_between_title_and_data
        workbook = self.writer.book
        worksheet = self.writer.sheets[sheet_name]
        if create_plots:
            self.Insert_Graphs_To_Excel(insert_row=row, group_average=group_mean_data_df, group_half_error=group_half_error,
              average_startrow=average_data_start_row,
              error_startrow=half_error_start_row,
              data_type=data_type,
              y_axis_label=y_axis_label,
              worksheet=worksheet,
              workbook=workbook,
              negative_error_row=negative_error_row,
              sheet_name=sheet_name)
        worksheet.set_column("A:A", 45)
        worksheet = self.writer.sheets["Normalized_Data"]
        worksheet.set_column("A:A", 45)

    def OnPrismOpen(self, e):
        previous_file_status = self.input_prism_file_okay
        self.input_prism_file_okay = True
        dlg = wx.FileDialog(self, message="Select a .pzfx File", style=(wx.FD_OPEN))
        if dlg.ShowModal() == wx.ID_OK:
            self.prism_file_path = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
        if previous_file_status:
            self.input_prism_file_okay = True
            return
        else:
            self.input_prism_file_okay = False
            return
        if not re.match(".*\\.pzfx", self.prism_file_path):
            message = "The selected file is not the right type. It must be a .pzfx file."
            msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            self.input_prism_file_okay = False
            return
        self.prism_file_st.SetLabel(self.prism_file_path)

    def Create_Prism_File(self, e):
        if self.input_data_file_okay == False:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        else:
            if self.input_prism_file_okay == False:
                message = "Please select a valid Prism file."
                msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
                return
            else:
                if len(self.groups) == 0:
                    message = "Please create some groups."
                    msg_dlg = wx.MessageDialog(None, message, "No Groups", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
                    return
                else:
                    normalizing_compounds = list(self.compounds_listbox.GetCheckedStrings())
                    if len(normalizing_compounds) > 0:
                        normalized_data_df = self.data_df.copy(deep=True)
                        normalized_compound_data = self.data_df.loc[normalizing_compounds]
                        for normalizing_compound in normalizing_compounds:
                            for sample in self.data_df.columns:
                                normalized_data_df.loc[:, sample] = normalized_data_df.loc[:, sample] / normalized_compound_data.loc[(normalizing_compound, sample)]

                    else:
                        normalized_data_df = self.data_df
                group_mean_data_df = pandas.DataFrame()
                group_error_data_df = pandas.DataFrame()
                for group_name, samples in self.groups.items():
                    group_mean_data_df.loc[:, group_name] = normalized_data_df.loc[:, samples].mean(axis=1)
                    if self.current_error_type == "STD":
                        group_error_data_df.loc[:, group_name] = normalized_data_df.loc[:, samples].std(axis=1)
                    else:
                        group_error_data_df.loc[:, group_name] = normalized_data_df.loc[:, samples].sem(axis=1)

                prism_tree = ET.parse(self.prism_file_path)
                root = prism_tree.getroot()
                table_sequence = None
                table_sequence = prism_tree.find("TableSequence")
                if table_sequence == None:
                    message = "The selected Prism file is not formatted as expected. Make sure it is the correct type of Prism file and try again."
                    msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
                    return
                for ref in table_sequence.findall("Ref"):
                    table_sequence.remove(ref)

                ET.SubElement(table_sequence, "Ref", {'ID':"Table1",  'Selected':"1"})
                for i in range(2, len(group_mean_data_df) + 1):
                    ET.SubElement(table_sequence, "Ref", {"ID": ("Table" + str(i))})

                table_attributes = None
                row_titles_attributes = None
                ycolumn_attributes = None
                table = None
                table = prism_tree.find("Table")
                if not table == None:
                    table_attributes = table.attrib
                    row = None
                    row = table.find("RowTitlesColumn")
                    if not row == None:
                        row_titles_attributes = row.attrib
                    ycolumn = None
                    ycolumn = table.find("YColumn")
                    if not ycolumn == None:
                        ycolumn_attributes = ycolumn.attrib
                    for table in root.findall("Table"):
                        root.remove(table)

                    for i in range(1, len(group_mean_data_df) + 1):
                        compound = group_mean_data_df.index[i - 1]
                        if table_attributes == None:
                            attributes = {"ID": ("Table" + str(i))}
                        else:
                            attributes = table_attributes
                            attributes.update({"ID": ("Table" + str(i))})
                        table_element = ET.SubElement(root, "Table", attributes)
                        title_element = ET.SubElement(table_element, "Title")
                        title_element.text = compound
                        for group, samples in self.groups.items():
                            if ycolumn_attributes == None:
                                attributes = {}
                            else:
                                attributes = ycolumn_attributes
                            ycolumn_element = ET.SubElement(table_element, "YColumn", attributes)
                            title_element = ET.SubElement(ycolumn_element, "Title")
                            title_element.text = group
                            subcolumn_element = ET.SubElement(ycolumn_element, "Subcolumn")
                            d_element = ET.SubElement(subcolumn_element, "d")
                            d_element.text = str(group_mean_data_df.loc[(compound, group)])
                            subcolumn_element = ET.SubElement(ycolumn_element, "Subcolumn")
                            d_element = ET.SubElement(subcolumn_element, "d")
                            d_element.text = str(group_error_data_df.loc[(compound, group)])
                            subcolumn_element = ET.SubElement(ycolumn_element, "Subcolumn")
                            d_element = ET.SubElement(subcolumn_element, "d")
                            d_element.text = str(len(samples))

                    dlg = wx.FileDialog(self,
                      message="Save file as ...", defaultDir=(self.data_directory_path),
                      defaultFile="",
                      style=(wx.FD_SAVE))
                    if dlg.ShowModal() == wx.ID_OK:
                        path = dlg.GetPath()
                        dlg.Destroy()
                else:
                    dlg.Destroy()
                return
            path = re.match(".*\\.pzfx", path) or path + ".pzfx"
        prism_tree.write(path, encoding="UTF-8", xml_declaration=True)


def main():
    ex = wx.App(False)
    Prism_Populator_GUI(None, title="Prism Populator")
    ex.MainLoop()


if __name__ == "__main__":
    main()
