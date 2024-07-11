
# uncompyle6 version 3.9.1
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.11.9 (main, Apr  2 2024, 08:25:04) [Clang 15.0.0 (clang-1500.3.9.4)]
# Embedded file name: Prism_Populator.py
import wx
import wx.lib.agw.genericmessagedialog as GMD
import pandas as pd
from lxml import etree as ET
import pandas, re
from collections import OrderedDict
import os
from xlsxwriter.utility import xl_rowcol_to_cell
import numpy as np
import sys, traceback
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
        self.writer = None
        #self.unique_pixels = []  # Define unique_pixels here
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
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        radio_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.error_radio_box = wx.RadioBox(panel, label="Error Calculation, Relative and Fractional", choices=["SEM", "STD", "RELATIVE", "FRACTION"], pos=(0, 0), majorDimension=1, style=(wx.RA_SPECIFY_ROWS))
        self.error_radio_box.SetSelection(0)
        self.current_error_type = "SEM"
        self.error_radio_box.Bind(wx.EVT_RADIOBOX, self.onErrorRadioBox)
        radio_box_sizer.Add((self.error_radio_box), flag=(wx.ALIGN_LEFT | wx.LEFT), border=10)
        vbox.Add(radio_box_sizer)
        # radio_box_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        # self.radio_box = wx.RadioBox(panel, label="Relative and Fraction", choices=["RELATIVE AND FRACTION"], pos=(175, 0), majorDimension=1, style=(wx.RA_SPECIFY_ROWS))
        # self.radio_box.Bind(wx.EVT_RADIOBOX, self.onErrorRadioBox)
        # self.radio_box.Enable(False)
        # radio_box_sizer2.Add((self.radio_box), flag=(wx.ALIGN_LEFT | wx.LEFT), border=10)
        # hbox.Add(radio_box_sizer2)
        
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

        # Add Compounds start from dropdown
        compounds_label = wx.StaticText(panel, label="Normalizing Compounds Start From:")
        self.compounds_dropdown = wx.ComboBox(panel, style=wx.CB_READONLY)
        vbox.Add(compounds_label, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.TOP), border=10)
        vbox.Add(self.compounds_dropdown, flag=(wx.ALIGN_LEFT | wx.LEFT), border=10)

        line = wx.StaticLine(panel)
        vbox.Add(line, flag=(wx.EXPAND | wx.LEFT | wx.RIGHT), border=10)
        sizer = wx.FlexGridSizer(2, 4, 0, 10)
        st1 = wx.StaticText(panel, label="Groups")
        st2 = wx.StaticText(panel, label="Samples")
        st3 = wx.StaticText(panel, label="Pixels")
        st4 = wx.StaticText(panel, label="Normalizing Compounds")
        sizer.Add(st1)
        sizer.Add(st2)
        sizer.Add(st3)
        sizer.Add(st4)
        self.groups_listbox = wx.ListBox(panel, style=(wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB))
        self.groups_listbox.SetMinSize((250, 200))
        self.groups_listbox.Bind(wx.EVT_LISTBOX, self.onGroupListBox)
        sizer.Add((self.groups_listbox), flag=(wx.EXPAND))
        self.samples_listbox = wx.ListBox(panel, style=(wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB | wx.LB_SORT))
        self.samples_listbox.SetMinSize((250, 200))
        self.samples_listbox.Bind(wx.EVT_LISTBOX, self.onSampleListBox)
        sizer.Add((self.samples_listbox), flag=(wx.EXPAND))
        self.pixels_listbox = wx.ListBox(panel, style=(wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB))
        self.pixels_listbox.SetMinSize((250, 200))
        sizer.Add((self.pixels_listbox), flag=(wx.EXPAND))
        self.compounds_listbox = wx.CheckListBox(panel, style=(wx.LB_SORT))
        self.compounds_listbox.SetMinSize((250, 200))
        sizer.Add((self.compounds_listbox), flag=(wx.EXPAND))
        sizer.AddGrowableCol(0, 1)
        sizer.AddGrowableCol(1, 1)
        sizer.AddGrowableCol(2, 1)
        sizer.AddGrowableCol(3, 1)
        sizer.AddGrowableRow(1, 1)
        vbox.Add(sizer, proportion=1, flag=(wx.EXPAND | wx.ALL), border=10)
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
        add_pixel_button = wx.Button(panel, label="Add Pixel")
        add_pixel_button.Bind(wx.EVT_BUTTON, self.Add_Pixel)
        delete_pixel_button = wx.Button(panel, label="Delete Pixel")
        delete_pixel_button.Bind(wx.EVT_BUTTON, self.Delete_Pixel)
        group_buttons_hbox = wx.BoxSizer(wx.HORIZONTAL)
        group_buttons_hbox.Add(add_group_button, flag=(wx.RIGHT | wx.TOP | wx.BOTTOM), border=5)
        group_buttons_hbox.Add(delete_group_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(move_group_up_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(move_group_down_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(add_sample_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(delete_sample_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(add_pixel_button, flag=(wx.ALL), border=5)
        group_buttons_hbox.Add(delete_pixel_button, flag=(wx.ALL), border=5)        
        vbox.Add(group_buttons_hbox, flag=(wx.ALIGN_LEFT | wx.ALL), border=10)
        plot_buttons_header = wx.StaticText(panel, label="Populate Data:")
        vbox.Add(plot_buttons_header, flag=(wx.ALIGN_LEFT | wx.LEFT | wx.TOP), border=10)
        run_button = wx.Button(panel, label="Create Prism File")
        run_button.Bind(wx.EVT_BUTTON, self.Create_Prism_File)
        create_excel_plots_button = wx.Button(panel, label="Create Excel Plots")
        create_excel_plots_button.Bind(wx.EVT_BUTTON, self.Save_Plot_Data)
        # save_plot_data_button = wx.Button(panel, label="Save Plot Data")
        # save_plot_data_button.Bind(wx.EVT_BUTTON, self.Save_Plot_Data)
        plot_buttons_hbox = wx.BoxSizer(wx.HORIZONTAL)
        plot_buttons_hbox.Add(run_button, flag=(wx.RIGHT | wx.TOP | wx.BOTTOM), border=5)
        plot_buttons_hbox.Add(create_excel_plots_button, flag=(wx.ALL), border=5)
        # plot_buttons_hbox.Add(save_plot_data_button, flag=(wx.ALL), border=5)
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
    def onGroupListBox(self, event):
        selected_group = self.groups_listbox.GetStringSelection()
        if selected_group:
            samples_dict = self.groups[selected_group]
            samples_list = list(samples_dict.keys())
            self.samples_listbox.Set(samples_list)
    def onSampleListBox(self, event):
        selected_sample = self.samples_listbox.GetStringSelection()
        selected_group = self.groups_listbox.GetStringSelection()
        if selected_group and selected_sample:
            self.updatePixelListBox(selected_group, selected_sample)
    def updatePixelListBox(self, selected_group, selected_sample):
        if selected_group in self.groups and selected_sample in self.groups[selected_group]:
            pixels_list = self.groups[selected_group][selected_sample]
            # Ensure we are working with a dictionary containing 'pixels' key
            if isinstance(pixels_list, list):
                pixels_list = [str(pixels) for pixels in pixels_list]
            else:
                pixels_list = [str(pixels_list)]
            self.pixels_listbox.Set(pixels_list)

    def Update_Group_List(self):
        """"""
        self.groups_listbox.Set(list(self.groups.keys()))
        
    def get_pixel_values_for_sample(self, sample):
        # Filter the DataFrame to get the rows corresponding to the sample
        sample_data = self.data_df[self.data_df['tissue_id'] == sample]
        # Create z values by concatenating x and y coordinates as strings
        pixel_values = (sample_data['x'].astype(str) + "_" + sample_data['y'].astype(str)).tolist()
        
        return pixel_values
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
            
            # Get group name from user
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
                    # dlg.Destroy()
                    return
            
            selections = []
            # Get sample selections from user
            while len(selections) == 0:
                sample_names = self.unique_tissue_ids
                dlg = wx.MultiChoiceDialog(None, "Select the samples in group " + group_name + ":", 'Samples in Group "' + group_name + '"', sample_names)
                if dlg.ShowModal() == wx.ID_OK:
                    selections = dlg.GetSelections()
                    if len(selections) != 0:
                        selected_samples = [sample_names[x] for x in selections]
                    else:
                        message = "Please select at least one sample for the group."
                        msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
                        msg_dlg.ShowModal()
                        msg_dlg.Destroy()
                    dlg.Destroy()
                else:
                    # dlg.Destroy()
                    return
            # Initialize group with empty z values for each selected sample
            self.groups[group_name] = {sample: [] for sample in selected_samples}
            
            # # For each selected sample, present a dialog to select z values
            # for sample in selected_samples:
            #     pixel_values = self.get_pixel_values_for_sample(sample)  # Get z values for the sample
            #     if pixel_values:
            #         pixel_selections = []
            #         while len(pixel_selections) == 0:
            #             dlg = wx.MultiChoiceDialog(None, f"Select the pixel values for sample {sample}:", f'Pixel values in Sample "{sample}"', pixel_values)
            #             if dlg.ShowModal() == wx.ID_OK:
            #                 pixel_selections = dlg.GetSelections()
            #                 if len(pixel_selections) != 0:
            #                     self.groups[group_name][sample] = [pixel_values[x] for x in pixel_selections]
            #                 else:
            #                     message = "Please select at least one pixel value for the sample."
            #                     msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
            #                     msg_dlg.ShowModal()
            #                     msg_dlg.Destroy()
            #                 dlg.Destroy()
            #             else:
            #                 dlg.Destroy()
            #                 return
                        
            for sample in selected_samples:
                pixel_values = self.get_pixel_values_for_sample(sample)  # Get pixel values for the sample
                if pixel_values:
                    select_all_checked = True  # Default select all to checked
                    dlg = wx.MultiChoiceDialog(None, f"Select the pixel values for sample {sample}:", f'Pixel values in Sample "{sample}"', pixel_values)
                    dlg.SetSelections(list(range(len(pixel_values))))  # Select all by default
                    def on_check(event):
                        if checkbox.IsChecked():
                            dlg.SetSelections(list(range(len(pixel_values))))  # Select all if checked
                        else:
                            dlg.SetSelections([])  # Clear selection if unchecked
                    dlg_sizer = dlg.GetSizer()
                    checkbox = wx.CheckBox(dlg, label="Select All")
                    checkbox.SetValue(select_all_checked)
                    checkbox.Bind(wx.EVT_CHECKBOX, on_check)
                    dlg_sizer.Insert(0, checkbox, flag=wx.ALL, border=5)
                    dlg_sizer.Fit(dlg)
                    if dlg.ShowModal() == wx.ID_OK:
                        pixel_selections = dlg.GetSelections()
                        if pixel_selections:
                            self.groups[group_name][sample] = [pixel_values[x] for x in pixel_selections]
                        else:
                            message = "Please select at least one pixel value for the sample."
                            msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
                            msg_dlg.ShowModal()
                            msg_dlg.Destroy()
                    dlg.Destroy()
                    # if not dlg.ShowModal() == wx.ID_OK:
                    #     dlg.Destroy()
                    #     return
                    # dlg.Destroy()

            if len(self.groups) > initial_groups_length:
                self.Update_Group_List()

    def Delete_Group(self, event):
        if not self.input_data_file_okay:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        
        if len(self.groups) == 0:
            message = "There are no groups to delete."
            msg_dlg = wx.MessageDialog(None, message, "No Groups To Delete", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        
        selected_group_index = self.groups_listbox.GetSelection()
        if selected_group_index != wx.NOT_FOUND:
            selected_group = self.groups_listbox.GetString(selected_group_index)
            self.groups.pop(selected_group)
            self.Update_Group_List()
            
            if len(self.groups) > 0:
                if selected_group_index < len(self.groups):
                    self.groups_listbox.SetSelection(selected_group_index)
                else:
                    self.groups_listbox.SetSelection(selected_group_index - 1)
                selected_group = self.groups_listbox.GetStringSelection()
                self.samples_listbox.Set(list(self.groups[selected_group].keys()))
                
                # Update the pixels listbox based on the selected group and sample
                selected_sample = self.samples_listbox.GetStringSelection()
                if selected_sample and selected_sample in self.groups[selected_group]:
                    self.pixels_listbox.Set(self.groups[selected_group][selected_sample])
                else:
                    self.pixels_listbox.Clear()
            else:
                self.samples_listbox.Clear()
                self.pixels_listbox.Clear()
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
        if not self.input_data_file_okay:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        selected_group = self.groups_listbox.GetStringSelection()
        if selected_group:
            # Initialize the group if it doesn't exist
            if selected_group not in self.groups:
                self.groups[selected_group] = {}
            # Get the list of tissue_ids not already in the selected group
            samples_to_display = [sample for sample in self.unique_tissue_ids if sample not in self.groups[selected_group]]
            if samples_to_display:
                dlg = wx.MultiChoiceDialog(None, f"Select the samples to add to group {selected_group}:", f'Add Samples To Group "{selected_group}"', samples_to_display)
                if dlg.ShowModal() == wx.ID_OK:
                    selections = dlg.GetSelections()
                    if selections:
                        selected_samples = [samples_to_display[x] for x in selections]
                        for sample in selected_samples:
                            pixels = self.get_pixel_values_for_sample(sample)  # Get pixel values for the sample
                            if pixels:
                                select_all_checked = True  # Default select all to checked
                                pixel_dlg = wx.MultiChoiceDialog(None, f"Select the pixel values for sample {sample}:", f'Pixel values in Sample "{sample}"', pixels)
                                pixel_dlg.SetSelections(list(range(len(pixels))))  # Select all by default

                                def on_check(event):
                                    if checkbox.IsChecked():
                                        pixel_dlg.SetSelections(list(range(len(pixels))))  # Select all if checked
                                    else:
                                        pixel_dlg.SetSelections([])  # Clear selection if unchecked

                                pixel_dlg_sizer = pixel_dlg.GetSizer()
                                checkbox = wx.CheckBox(pixel_dlg, label="Select All")
                                checkbox.SetValue(select_all_checked)
                                checkbox.Bind(wx.EVT_CHECKBOX, on_check)
                                pixel_dlg_sizer.Insert(0, checkbox, flag=wx.ALL, border=5)
                                pixel_dlg_sizer.Fit(pixel_dlg)

                                if pixel_dlg.ShowModal() == wx.ID_OK:
                                    pixel_selections = pixel_dlg.GetSelections()
                                    if pixel_selections:
                                        self.groups[selected_group][sample] = [pixels[x] for x in pixel_selections]
                                    else:
                                        message = "Please select at least one pixel value for the sample."
                                        msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
                                        msg_dlg.ShowModal()
                                        msg_dlg.Destroy()
                                pixel_dlg.Destroy()
                        # Update the samples listbox to reflect the new samples added to the group
                        self.samples_listbox.Set(list(self.groups[selected_group].keys()))
                    else:
                        message = "No samples selected to add."
                        msg_dlg = wx.MessageDialog(None, message, "No Samples Selected", wx.OK | wx.ICON_EXCLAMATION)
                        msg_dlg.ShowModal()
                        msg_dlg.Destroy()
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
        if not self.input_data_file_okay:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        selected_group = self.groups_listbox.GetStringSelection()
        if selected_group:
            sample_to_delete = self.samples_listbox.GetStringSelection()
            index_of_selection = self.samples_listbox.GetSelection()
            if sample_to_delete != wx.NOT_FOUND and sample_to_delete:
                if len(self.groups[selected_group]) == 1:
                    message = "Groups must contain at least one sample."
                    msg_dlg = wx.MessageDialog(None, message, "Not Enough Samples", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
                else:
                    del self.groups[selected_group][sample_to_delete]
                    self.samples_listbox.Set(list(self.groups[selected_group].keys()))
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

    def Add_Pixel(self, event):
        if not self.input_data_file_okay:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        
        selected_group = self.groups_listbox.GetStringSelection()
        selected_sample = self.samples_listbox.GetStringSelection()
        
        if selected_group and selected_sample:
            if selected_group in self.groups and selected_sample in self.groups[selected_group]:
                # Ensure self.unique_pixels is populated with the unique pixel values
                self.unique_pixels = self.get_pixel_values_for_sample(selected_sample)
                pixels = list(self.unique_pixels)
                
                # Remove existing pixels from the list of available pixels to add
                existing_pixels = self.groups[selected_group][selected_sample]
                pixels_to_add = [pixel for pixel in pixels if pixel not in existing_pixels]
                
                if pixels_to_add:
                    dlg = wx.MultiChoiceDialog(None, f"Select pixels to add to sample {selected_sample}:", 'Add Pixels', pixels_to_add)
                    if dlg.ShowModal() == wx.ID_OK:
                        selections = dlg.GetSelections()
                        if selections:
                            for index in selections:
                                pixel_to_add = pixels_to_add[index]
                                self.groups[selected_group][selected_sample].append(pixel_to_add)
                            self.pixels_listbox.Set(self.groups[selected_group][selected_sample])
                    dlg.Destroy()
                else:
                    message = "All pixels are already added to the sample."
                    msg_dlg = wx.MessageDialog(None, message, "No More Pixels", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
            else:
                message = f"Sample {selected_sample} not found in group {selected_group}."
                msg_dlg = wx.MessageDialog(None, message, "Sample Not Found", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
        else:
            message = "No sample or group selected."
            msg_dlg = wx.MessageDialog(None, message, "No Sample or Group Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()


    def Delete_Pixel(self, event):
        if not self.input_data_file_okay:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        
        selected_group = self.groups_listbox.GetStringSelection()
        selected_sample = self.samples_listbox.GetStringSelection()
        if selected_group and selected_sample:
            if selected_group in self.groups and selected_sample in self.groups[selected_group]:
                # Convert the list to a dictionary if needed
                if isinstance(self.groups[selected_group][selected_sample], list):
                    self.groups[selected_group][selected_sample] = {'pixels': self.groups[selected_group][selected_sample]}
                
                selected_pixel = self.pixels_listbox.GetStringSelection()
                index_of_selection = self.pixels_listbox.GetSelection()
                if selected_pixel != wx.NOT_FOUND and selected_pixel:
                    if len(self.groups[selected_group][selected_sample].get('pixels', [])) == 1:
                        message = "Samples must contain at least one pixel."
                        msg_dlg = wx.MessageDialog(None, message, "Not Enough Pixels", wx.OK | wx.ICON_EXCLAMATION)
                        msg_dlg.ShowModal()
                        msg_dlg.Destroy()
                    else:
                        self.groups[selected_group][selected_sample]['pixels'].remove(selected_pixel)
                        self.pixels_listbox.Set(self.groups[selected_group][selected_sample]['pixels'])
                        if index_of_selection < len(self.groups[selected_group][selected_sample]['pixels']):
                            self.pixels_listbox.SetSelection(index_of_selection)
                        else:
                            self.pixels_listbox.SetSelection(index_of_selection - 1)
                else:
                    message = "No pixel selected."
                    msg_dlg = wx.MessageDialog(None, message, "No Pixel Selected", wx.OK | wx.ICON_EXCLAMATION)
                    msg_dlg.ShowModal()
                    msg_dlg.Destroy()
            else:
                message = f"Sample {selected_sample} not found in group {selected_group}."
                msg_dlg = wx.MessageDialog(None, message, "Sample Not Found", wx.OK | wx.ICON_EXCLAMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
        else:
            message = "No sample or group selected."
            msg_dlg = wx.MessageDialog(None, message, "No Sample or Group Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()

    def OnCompoundsDropdown(self, event):
        selected_column = self.compounds_dropdown.GetValue()
        start_index = self.data_df.columns.get_loc(selected_column)
        normalization_columns = self.data_df.columns[start_index:]
        self.compounds_listbox.Set(normalization_columns)
  
    def OnDataOpen(self, e):
        previous_file_status = self.input_data_file_okay
        self.input_data_file_okay = True
        data_sheet = 0
        dlg = wx.FileDialog(self, message="Select Excel or csv File", style=(wx.FD_OPEN))
        if dlg.ShowModal() == wx.ID_OK:
            self.data_file_path = dlg.GetPath()
            self.data_file_st.SetLabel(self.data_file_path)
            
            # Load the Excel or CSV file and initialize data_df
            try:
                file_extension = os.path.splitext(self.data_file_path)[1].lower()
                if file_extension in [".xlsx", ".xlsm", ".xls"]:
                    self.data_df = pd.read_excel(self.data_file_path, engine='openpyxl' if file_extension == '.xlsx' else 'xlrd')
                elif file_extension == ".csv":
                    self.data_df = pd.read_csv(self.data_file_path)
                else:
                    raise ValueError("Unsupported file format.")
                
                # Validate the data
                if len(self.data_df.columns) > len(self.data_df.columns.unique()):
                    raise ValueError("Duplicate column names found in the data file.")
                
                dlg.Destroy()
            except Exception as exc:
                self.input_data_file_okay = False
                msg_dlg = wx.MessageDialog(self, message=f"Failed to load data file: {exc}", caption="Error", style=wx.OK | wx.ICON_ERROR)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()
                dlg.Destroy()
                return
        else:
            dlg.Destroy()
            if previous_file_status:
                self.input_data_file_okay = True
                return
            else:
                self.input_data_file_okay = False
                return
        self.input_data_file_okay = True
        if not re.match(".*\\.xlsx|.*\\.xlsm|.*\\.xls|.*\\.csv", self.data_file_path):
            message = "The selected file is not the right type."
            msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            self.input_data_file_okay = False
            return
        if re.match(".*\\.xlsx|.*\\.xlsm|.*\\.xls", self.data_file_path):
            workbook = pd.ExcelFile(self.data_file_path)
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
            self.data_df = pd.read_excel(workbook, sheet_name=data_sheet)
        else:
            self.data_df = pd.read_csv(self.data_file_path)
        # Initialize unique_pixels from the data file
        if 'pixel' in self.data_df.columns:
            self.unique_pixels = self.data_df['pixel'].unique().tolist()
        else:
            self.unique_pixels = []
        # Do not aggregate by mean since we need individual rows for each tissue_id
        # self.process_data()
        # Update the GUI components
        self.sample_names = list(self.data_df.columns)
        # Assuming self.data_df is your DataFrame
        self.tissue_names = self.data_df['tissue_id'].astype(str).unique().tolist()
        self.data_file_st.SetLabel(self.data_file_path)
        self.data_directory_path = os.path.split(self.data_file_path)[0]
        self.groups = OrderedDict()
        self.groups_listbox.Clear()
        self.samples_listbox.Clear()
        self.compounds_listbox.Clear()

        # Populate the compounds dropdown with column names
        column_names = self.data_df.columns.tolist()
        self.compounds_dropdown.Set(column_names)
        
        # Bind event to update compounds_listbox when a selection is made in the dropdown
        self.compounds_dropdown.Bind(wx.EVT_COMBOBOX, self.OnCompoundsDropdown)
        
        self.unique_tissue_ids = self.data_df['tissue_id'].unique().astype(str).tolist()
        
        # # Update the compounds listbox with normalization columns
        # normalization_columns = self.data_df.columns[8:]  # Select all columns starting from the 9th column
        # self.compounds_listbox.Set(normalization_columns)
        
        # # Update the groups listbox with unique tissue_id values
        # self.unique_tissue_ids = self.data_df['tissue_id'].unique().astype(str).tolist()  # Store unique tissue IDs as list of strings

    def Save_Plot_Data(self, event):
        """"""
        group_dataframe = pandas.DataFrame(index=(self.tissue_names ), columns=(self.groups.keys()))
        print(group_dataframe)
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
        # self.writer.save()
        self.writer.close()  # Use close instead of save
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
                elif type(int_or_slice) == np.ndarray:
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

        # # Get normalization compounds based on the selected column from the dropdown
        # selected_column = self.compounds_dropdown.GetValue()
        # start_index = self.data_df.columns.get_loc(selected_column)
        # normalizing_compounds = self.data_df.columns[start_index:]

        # Get normalization compounds (columns selected from the compounds_listbox)
        normalizing_compounds = [self.compounds_listbox.GetString(i) for i in range(self.compounds_listbox.GetCount()) if self.compounds_listbox.IsChecked(i)]


        # normalizing_compounds = [col for col in self.data_df.columns]
        # Initialize normalized data dataframe
        normalized_data_df = pd.DataFrame()
        # Normalize the data
        for group_name, samples in self.groups.items():
            sample_ids = list(samples.keys()) if isinstance(samples, dict) else samples
            for sample_id in sample_ids:
                pixels_list = self.groups[group_name][sample_id]
                selected_data = self.data_df[self.data_df['tissue_id'] == sample_id]
                columns_to_select = ['tissue_id', 'x', 'y'] + list(normalizing_compounds)
                selected_data = selected_data[columns_to_select]
                selected_data['pixel'] = selected_data['x'].astype(str) + "_" + selected_data['y'].astype(str)
                selected_data = selected_data[selected_data['pixel'].isin(pixels_list)]
                tissue_sum = selected_data[normalizing_compounds].sum()
                for column in normalizing_compounds:
                    selected_data[column] = selected_data[column] / tissue_sum[column]
                selected_data['group_name'] = group_name
                selected_data['sample_id'] = sample_id
                normalized_data_df = pd.concat([normalized_data_df, selected_data], ignore_index=True)
        columns_to_exclude = ['tissue_id', 'x', 'y', 'pixel', 'group_name', 'sample_id']
        numeric_columns = normalized_data_df.columns.difference(columns_to_exclude)
        # Calculate mean and error for each sample and group
        sample_mean_data_df = pd.DataFrame(columns=['group_name', 'sample_id'] + list(numeric_columns))
        sample_error_data_df = pd.DataFrame(columns=['group_name', 'sample_id'] + list(numeric_columns))
        for group_name, samples in self.groups.items():
            sample_ids = list(samples.keys()) if isinstance(samples, dict) else samples
            group_data = normalized_data_df[normalized_data_df['group_name'] == group_name]
            relative_data_df = self.data_df[self.data_df['tissue_id'].isin(sample_ids)]
            # Calculate total sum for each compound in the group from the original data
            original_group_data = pd.DataFrame(columns=numeric_columns)
            for sample_id in sample_ids:
                sample_original_data = relative_data_df[relative_data_df['tissue_id'] == sample_id]
                sample_original_data['pixel'] = sample_original_data['x'].astype(str) + "_" + sample_original_data['y'].astype(str)
                pixels_list = self.groups[group_name][sample_id]
                sample_original_data = sample_original_data[sample_original_data['pixel'].isin(pixels_list)]
                sample_sum = sample_original_data[numeric_columns].sum()
                original_group_data = pd.concat([original_group_data, pd.DataFrame([sample_sum])], ignore_index=True)
            group_total_sum = original_group_data.sum()
            for sample_id in sample_ids:
                pixels_list = self.groups[group_name][sample_id]
                sample_group_data = group_data[group_data['sample_id'] == sample_id]
                sample_relative_data = relative_data_df[relative_data_df['tissue_id'] == sample_id]
                sample_relative_data['pixel'] = sample_relative_data['x'].astype(str) + "_" + sample_relative_data['y'].astype(str)
                sample_relative_data = sample_relative_data[sample_relative_data['pixel'].isin(pixels_list)]
                sample_mean_data = {'group_name': group_name, 'sample_id': sample_id}
                sample_error_data = {'group_name': group_name, 'sample_id': sample_id}
                for column in numeric_columns:
                    sample_mean_data[column] = sample_group_data[column].mean()
                    if self.current_error_type == "STD":
                        sample_error_data[column] = sample_group_data[column].std()
                    elif self.current_error_type == "SEM":
                        sample_error_data[column] = sample_group_data[column].sem()
                    elif self.current_error_type == "FRACTION":
                        sample_original_sum = sample_relative_data[column].sum()
                        sample_error_data[column] = sample_original_sum / group_total_sum[column]
                    elif self.current_error_type == "RELATIVE":
                        sample_error_data[column] = np.abs(sample_relative_data[column].sum())
                sample_mean_data_df = pd.concat([sample_mean_data_df, pd.DataFrame([sample_mean_data])], ignore_index=True)
                sample_error_data_df = pd.concat([sample_error_data_df, pd.DataFrame([sample_error_data])], ignore_index=True)
        # Write dataframes to Excel
        tables_to_print = [sample_mean_data_df, sample_error_data_df]
        # table_titles = ['Sample Mean Data', 'Sample Error Data']
        dlg = wx.FileDialog(self, message="Save file as ...", defaultDir=self.data_directory_path, defaultFile="", style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        if not re.match(".*\\.xlsx", path):
            path = path + ".xlsx"
        # Initialize the writer here
        self.writer = pd.ExcelWriter(path, engine="xlsxwriter")
        row = 0
        average_data_start_row = 0  # Initialize with a default value
        for i in range(len(tables_to_print)):
            self.Write_DF_To_Excel(table_titles[i], startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data, dataframe=tables_to_print[i])
            if table_titles[i] == average_table_title:
                average_data_start_row = row + rows_between_title_and_data
            row = row + len(tables_to_print[i]) + rows_between_title_and_data + rows_between_dfs

        # Chunk the DataFrame if it exceeds the column limit
        def chunk_dataframe(df, chunk_size):
            for i in range(0, df.shape[1], chunk_size):
                yield df.iloc[:, i:i + chunk_size]

        # Maximum number of columns allowed in Excel
        max_columns = 16384
        chunks = chunk_dataframe(normalized_data_df.transpose(), max_columns)
        chunk_index = 0

        for chunk in chunks:
            # sheet_name="Normalized_Data"
            sheet_name_chunk = f"Normalized_Data_part{chunk_index+1}"
            self.Write_DF_To_Excel("Normalized Intensity", startrow=0, sheet_name=sheet_name_chunk, rows_between_title_and_data=rows_between_title_and_data, dataframe=chunk)
            chunk_index += 1

        # self.Write_DF_To_Excel("Normalized Intensity", startrow=0, sheet_name="Normalized_Data", rows_between_title_and_data=rows_between_title_and_data, dataframe=normalized_data_df.transpose())
        if create_plots:
            group_half_error = sample_error_data_df[numeric_columns] / 2
            group_half_error.loc["negative_error"] = 0
            self.Write_DF_To_Excel("Half " + self.current_error_type + " for Plots", startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data, dataframe=group_half_error)
            row = row + rows_between_title_and_data
            half_error_start_row = row
            negative_error_row = row + group_half_error.index.get_loc("negative_error") + 1 + len(group_half_error.columns.names)
            row = row + len(group_half_error) + rows_between_dfs
        self.Write_DF_To_Excel("Samples in Each Group", startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data, dataframe=group_dataframe)
        if len(normalizing_compounds) > 0:
            row = row + len(group_dataframe) + rows_between_title_and_data + rows_between_dfs
            normalizing_compounds_df = pd.DataFrame(index=normalizing_compounds)
            self.Write_DF_To_Excel("Normalizing Compounds", startrow=row, sheet_name=sheet_name, rows_between_title_and_data=rows_between_title_and_data, dataframe=normalizing_compounds_df)
            row = row + len(normalizing_compounds_df) + rows_between_graphs_and_data + rows_between_title_and_data
        workbook = self.writer.book
        worksheet = self.writer.sheets[sheet_name]
        if create_plots:
            self.Insert_Graphs_To_Excel(insert_row=row, group_average=sample_mean_data_df, group_half_error=group_half_error, average_startrow=average_data_start_row, error_startrow=half_error_start_row, data_type=data_type, y_axis_label=y_axis_label, worksheet=worksheet, workbook=workbook, negative_error_row=negative_error_row, sheet_name=sheet_name)
        worksheet.set_column("A:A", 45)
        # # Add the following line to create the "Normalized_Data" sheet before accessing it
        # self.writer.book.add_worksheet("Normalized_Data")
        # worksheet = self.writer.sheets["Normalized_Data"]
        # worksheet.set_column("A:A", 45)

        # Finalize the writer and save the file
        self.writer.close()

    def OnPrismOpen(self, e):
        previous_file_status = self.input_prism_file_okay
        self.input_prism_file_okay = True
        dlg = wx.FileDialog(self, message="Select a .pzfx File", style=(wx.FD_OPEN))
        if dlg.ShowModal() == wx.ID_OK:
            self.prism_file_path = dlg.GetPath()
            self.prism_file_st.SetLabel(self.prism_file_path)  # Update the label to display the selected file path
            dlg.Destroy()
        else:
            dlg.Destroy()
            if previous_file_status:
                self.input_prism_file_okay = True
                return
            else:
                self.input_prism_file_okay = False
                return
        # Additional validation can be added here if needed
        # For now, we assume that the selection of a valid file is sufficient
        if not re.match(".*\\.pzfx", self.prism_file_path):
            message = "The selected file is not the right type. It must be a .pzfx file."
            msg_dlg = wx.MessageDialog(None, message, "Warning", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            self.input_prism_file_okay = False
            return
        self.prism_file_st.SetLabel(self.prism_file_path)       
        self.input_prism_file_okay = True
    def Create_Prism_File(self, e):
        if not self.input_data_file_okay:
            message = "Please select a valid data file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        if not self.input_prism_file_okay:
            message = "Please select a valid Prism file."
            msg_dlg = wx.MessageDialog(None, message, "No File Selected", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        if len(self.groups) == 0:
            message = "Please create some groups."
            msg_dlg = wx.MessageDialog(None, message, "No Groups", wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return
        normalization_columns = list(self.compounds_listbox.GetCheckedStrings())
        normalized_data_df = pd.DataFrame()
        for group_name, samples in self.groups.items():
            sample_ids = list(samples.keys()) if isinstance(samples, dict) else samples
            for sample_id in sample_ids:
                pixels_list = self.groups[group_name][sample_id]
                selected_data = self.data_df[self.data_df['tissue_id'] == sample_id]
                columns_to_select = ['tissue_id', 'x', 'y'] + list(normalization_columns)
                selected_data = selected_data[columns_to_select]
                selected_data['pixel'] = selected_data['x'].astype(str) + "_" + selected_data['y'].astype(str)
                selected_data = selected_data[selected_data['pixel'].isin(pixels_list)]
                tissue_sum = selected_data[normalization_columns].sum()
                for column in normalization_columns:
                    selected_data[column] = selected_data[column] / tissue_sum[column]
                selected_data['group_name'] = group_name
                selected_data['sample_id'] = sample_id
                normalized_data_df = pd.concat([normalized_data_df, selected_data], ignore_index=True)
        columns_to_exclude = ['tissue_id', 'x', 'y', 'pixel', 'group_name', 'sample_id']
        numeric_columns = normalized_data_df.columns.difference(columns_to_exclude)
        print(normalized_data_df)
        sample_mean_data_df = pd.DataFrame(columns=['group_name', 'sample_id'] + list(numeric_columns))
        sample_error_data_df = pd.DataFrame(columns=['group_name', 'sample_id'] + list(numeric_columns))
        for group_name, samples in self.groups.items():
            sample_ids = list(samples.keys()) if isinstance(samples, dict) else samples
            group_data = normalized_data_df[normalized_data_df['group_name'] == group_name]
            relative_data_df = self.data_df[self.data_df['tissue_id'].isin(sample_ids)]
            # Calculate total sum for each compound in the group from the original data
            original_group_data = pd.DataFrame(columns=numeric_columns)
            for sample_id in sample_ids:
                sample_original_data = relative_data_df[relative_data_df['tissue_id'] == sample_id]
                sample_original_data['pixel'] = sample_original_data['x'].astype(str) + "_" + sample_original_data['y'].astype(str)
                pixels_list = self.groups[group_name][sample_id]
                sample_original_data = sample_original_data[sample_original_data['pixel'].isin(pixels_list)]
                sample_sum = sample_original_data[numeric_columns].sum()
                original_group_data = pd.concat([original_group_data, pd.DataFrame([sample_sum])], ignore_index=True)
            
            group_total_sum = original_group_data.sum()
            for sample_id in sample_ids:
                pixels_list = self.groups[group_name][sample_id]
                sample_group_data = group_data[group_data['sample_id'] == sample_id]
                sample_relative_data = relative_data_df[relative_data_df['tissue_id'] == sample_id]
                sample_relative_data['pixel'] = sample_relative_data['x'].astype(str) + "_" + sample_relative_data['y'].astype(str)
                sample_relative_data = sample_relative_data[sample_relative_data['pixel'].isin(pixels_list)]
                sample_mean_data = {'group_name': group_name, 'sample_id': sample_id}
                sample_error_data = {'group_name': group_name, 'sample_id': sample_id}
                for column in numeric_columns:
                    sample_mean_data[column] = sample_group_data[column].mean()
                    if self.current_error_type == "STD":
                        sample_error_data[column] = sample_group_data[column].std()
                    elif self.current_error_type == "SEM":
                        sample_error_data[column] = sample_group_data[column].sem()
                    elif self.current_error_type == "FRACTION":
                        sample_original_sum = sample_relative_data[column].sum()
                        sample_error_data[column] = sample_original_sum / group_total_sum[column]
                    elif self.current_error_type == "RELATIVE":
                        sample_error_data[column] = np.abs(sample_relative_data[column].sum())
                sample_mean_data_df = pd.concat([sample_mean_data_df, pd.DataFrame([sample_mean_data])], ignore_index=True)
                sample_error_data_df = pd.concat([sample_error_data_df, pd.DataFrame([sample_error_data])], ignore_index=True)
        print("Sample Mean Data:")
        print(sample_mean_data_df)
        print("Sample Error Data:")
        print(sample_error_data_df)
        try:
            prism_tree = ET.parse(self.prism_file_path)
            root = prism_tree.getroot()
            table_sequence = prism_tree.find("TableSequence")
            if table_sequence is None:
                raise ValueError("The selected Prism file is not formatted as expected.")
            for ref in table_sequence.findall("Ref"):
                table_sequence.remove(ref)
            for compound in normalization_columns:
                table_id = f"Table_{compound}"
                ET.SubElement(table_sequence, "Ref", {"ID": table_id, "Selected": "1"})
            for table in root.findall("Table"):
                root.remove(table)
            for compound in normalization_columns:
                table_id = f"Table_{compound}"
                table_element = ET.SubElement(root, "Table", {"ID": table_id})
                title_element = ET.SubElement(table_element, "Title")
                title_element.text = f"{compound}"
                for group_name, samples in self.groups.items():
                    for sample_id in samples:
                        ycolumn_element = ET.SubElement(table_element, "YColumn")
                        group_title_element = ET.SubElement(ycolumn_element, "Title")
                        group_title_element.text = f"{group_name} - {sample_id}"
                        subcolumn_error_element = ET.SubElement(ycolumn_element, "Subcolumn")
                        error_d_element = ET.SubElement(subcolumn_error_element, "d")
                        error_value = sample_error_data_df[(sample_error_data_df['group_name'] == group_name) & (sample_error_data_df['sample_id'] == sample_id)][compound].values[0]
                        error_d_element.text = "NaN" if pd.isna(error_value) else str(error_value)
                        subcolumn_n_element = ET.SubElement(ycolumn_element, "Subcolumn")
                        n_d_element = ET.SubElement(subcolumn_n_element, "d")
                        n_value = len(samples)
                        n_d_element.text = str(n_value)
            dlg = wx.FileDialog(self, message="Save file as ...", defaultDir=self.data_directory_path, defaultFile="", style=wx.FD_SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                save_path = dlg.GetPath()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            if not save_path.endswith(".pzfx"):
                save_path += ".pzfx"
            prism_tree.write(save_path, encoding="UTF-8", xml_declaration=True)
        except Exception as exc:
            msg_dlg = wx.MessageDialog(None, f"Failed to create Prism file: {exc}", "Error", wx.OK | wx.ICON_ERROR)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
 
def main():
    ex = wx.App(False)
    Prism_Populator_GUI(None, title="Prism Populator")
    ex.MainLoop()

if __name__ == "__main__":
    main()
