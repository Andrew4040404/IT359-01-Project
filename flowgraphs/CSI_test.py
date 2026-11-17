#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Wifi Analyzer
# Author: Max
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import ieee802_11
import osmosdr
import time
import sip
import threading



class CSI_test(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Wifi Analyzer", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Wifi Analyzer")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CSI_test")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.variable = variable = 2e7
        self.pilot_symbols = pilot_symbols = [[1, 1, 1, -1]]
        self.pilot_carriers = pilot_carriers = [[-21, -7, 7, 21]]
        self.occupied_carriers = occupied_carriers = [[-26, -25, -24, -23, -22, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10, -9, -8, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26]]
        self.constellation_object = constellation_object = digital.constellation_bpsk().base()
        self.constellation_object.set_npwr(1.0)
        self.WiFi_Channel = WiFi_Channel = 2.412e9
        self.WSS_Threshold = WSS_Threshold = 0.56
        self.WSL_sync_length = WSL_sync_length = 320
        self.RF_Gain = RF_Gain = False
        self.IF_Gain = IF_Gain = 24
        self.BB_Gain = BB_Gain = 20

        ##################################################
        # Blocks
        ##################################################

        self._WiFi_Channel_range = qtgui.Range(2.412e9, 2.484e9, 5e6, 2.412e9, 200)
        self._WiFi_Channel_win = qtgui.RangeWidget(self._WiFi_Channel_range, self.set_WiFi_Channel, "Wi-Fi 2.4 GHz Channels 1-14", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._WiFi_Channel_win)
        self._WSS_Threshold_range = qtgui.Range(0, 1, 0.01, 0.56, 200)
        self._WSS_Threshold_win = qtgui.RangeWidget(self._WSS_Threshold_range, self.set_WSS_Threshold, "Wi-Fi Short Squelch", "dial", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._WSS_Threshold_win)
        self._WSL_sync_length_range = qtgui.Range(160, 320, 160, 320, 200)
        self._WSL_sync_length_win = qtgui.RangeWidget(self._WSL_sync_length_range, self.set_WSL_sync_length, "Wi-Fi Sync Delay", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._WSL_sync_length_win)
        _RF_Gain_check_box = Qt.QCheckBox("+14db Internal AMP - DO NOT TOUCH")
        self._RF_Gain_choices = {True: 14, False: 0}
        self._RF_Gain_choices_inv = dict((v,k) for k,v in self._RF_Gain_choices.items())
        self._RF_Gain_callback = lambda i: Qt.QMetaObject.invokeMethod(_RF_Gain_check_box, "setChecked", Qt.Q_ARG("bool", self._RF_Gain_choices_inv[i]))
        self._RF_Gain_callback(self.RF_Gain)
        _RF_Gain_check_box.stateChanged.connect(lambda i: self.set_RF_Gain(self._RF_Gain_choices[bool(i)]))
        self.top_layout.addWidget(_RF_Gain_check_box)
        self._IF_Gain_range = qtgui.Range(0, 40, 8, 24, 25)
        self._IF_Gain_win = qtgui.RangeWidget(self._IF_Gain_range, self.set_IF_Gain, "LNA Gain", "dial", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._IF_Gain_win)
        self._BB_Gain_range = qtgui.Range(0, 50, 2, 20, 25)
        self._BB_Gain_win = qtgui.RangeWidget(self._BB_Gain_range, self.set_BB_Gain, "VGA Gain", "dial", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._BB_Gain_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_c(
            500, #size
            2e7, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            500, #size
            2e7, #samp_rate
            'Wi-Fi Short Monitor', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            64, #size
            'OFDM Constellation', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(2e7)
        self.osmosdr_source_0.set_center_freq(WiFi_Channel, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(RF_Gain, 0)
        self.osmosdr_source_0.set_if_gain(IF_Gain, 0)
        self.osmosdr_source_0.set_bb_gain(BB_Gain, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(2e7, 0)
        self.ieee802_11_sync_short_0 = ieee802_11.sync_short(WSS_Threshold, 2, False, False)
        self.ieee802_11_sync_long_0 = ieee802_11.sync_long(WSL_sync_length, False, False)
        self.ieee802_11_frame_equalizer_0 = ieee802_11.frame_equalizer(ieee802_11.LS, WiFi_Channel, 20e6, False, False)
        self.fft_vxx_0 = fft.fft_vcc(64, True, window.rectangular(64), True, 1)
        self.digital_ofdm_frame_equalizer_vcvc_0 = digital.ofdm_frame_equalizer_vcvc(digital.ofdm_equalizer_simpledfe(64, constellation_object, occupied_carriers, pilot_carriers, pilot_symbols), 4, '', True, 1)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, 64)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*64, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, 64)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*48)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_moving_average_xx_1 = blocks.moving_average_cc(48, 1, 4000, 1)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(64, 1, 4000, 1)
        self.blocks_keep_m_in_n_1 = blocks.keep_m_in_n(gr.sizeof_gr_complex, 26, 64, 33)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, 26, 64, 6)
        self.blocks_interleave_0 = blocks.interleave(gr.sizeof_gr_complex*1, 1)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_delay_1 = blocks.delay(gr.sizeof_gr_complex*1, WSL_sync_length)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, 16)
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_delay_0, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.ieee802_11_sync_short_0, 0))
        self.connect((self.blocks_delay_1, 0), (self.ieee802_11_sync_long_0, 1))
        self.connect((self.blocks_divide_xx_0, 0), (self.ieee802_11_sync_short_0, 2))
        self.connect((self.blocks_interleave_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_interleave_0, 0))
        self.connect((self.blocks_keep_m_in_n_1, 0), (self.blocks_interleave_0, 1))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_1, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_moving_average_xx_1, 0), (self.ieee802_11_sync_short_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_moving_average_xx_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.digital_ofdm_frame_equalizer_vcvc_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.blocks_keep_m_in_n_1, 0))
        self.connect((self.digital_ofdm_frame_equalizer_vcvc_0, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.ieee802_11_frame_equalizer_0, 0))
        self.connect((self.ieee802_11_frame_equalizer_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.ieee802_11_sync_long_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.ieee802_11_sync_short_0, 0), (self.blocks_delay_1, 0))
        self.connect((self.ieee802_11_sync_short_0, 0), (self.ieee802_11_sync_long_0, 0))
        self.connect((self.ieee802_11_sync_short_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.qtgui_time_sink_x_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "CSI_test")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_variable(self):
        return self.variable

    def set_variable(self, variable):
        self.variable = variable

    def get_pilot_symbols(self):
        return self.pilot_symbols

    def set_pilot_symbols(self, pilot_symbols):
        self.pilot_symbols = pilot_symbols

    def get_pilot_carriers(self):
        return self.pilot_carriers

    def set_pilot_carriers(self, pilot_carriers):
        self.pilot_carriers = pilot_carriers

    def get_occupied_carriers(self):
        return self.occupied_carriers

    def set_occupied_carriers(self, occupied_carriers):
        self.occupied_carriers = occupied_carriers

    def get_constellation_object(self):
        return self.constellation_object

    def set_constellation_object(self, constellation_object):
        self.constellation_object = constellation_object

    def get_WiFi_Channel(self):
        return self.WiFi_Channel

    def set_WiFi_Channel(self, WiFi_Channel):
        self.WiFi_Channel = WiFi_Channel
        self.ieee802_11_frame_equalizer_0.set_frequency(self.WiFi_Channel)
        self.osmosdr_source_0.set_center_freq(self.WiFi_Channel, 0)

    def get_WSS_Threshold(self):
        return self.WSS_Threshold

    def set_WSS_Threshold(self, WSS_Threshold):
        self.WSS_Threshold = WSS_Threshold

    def get_WSL_sync_length(self):
        return self.WSL_sync_length

    def set_WSL_sync_length(self, WSL_sync_length):
        self.WSL_sync_length = WSL_sync_length
        self.blocks_delay_1.set_dly(int(self.WSL_sync_length))

    def get_RF_Gain(self):
        return self.RF_Gain

    def set_RF_Gain(self, RF_Gain):
        self.RF_Gain = RF_Gain
        self._RF_Gain_callback(self.RF_Gain)
        self.osmosdr_source_0.set_gain(self.RF_Gain, 0)

    def get_IF_Gain(self):
        return self.IF_Gain

    def set_IF_Gain(self, IF_Gain):
        self.IF_Gain = IF_Gain
        self.osmosdr_source_0.set_if_gain(self.IF_Gain, 0)

    def get_BB_Gain(self):
        return self.BB_Gain

    def set_BB_Gain(self, BB_Gain):
        self.BB_Gain = BB_Gain
        self.osmosdr_source_0.set_bb_gain(self.BB_Gain, 0)




def main(top_block_cls=CSI_test, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
