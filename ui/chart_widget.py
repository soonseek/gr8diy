"""
캔들 차트 위젯 - PyQtGraph 버전
"""
import numpy as np
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, QRectF, QLineF, QDateTime
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
import pyqtgraph as pg
from collections import deque

# PyQtGraph 설정
try:
    pg.setConfigOptions(antialias=True)
    pg.setConfigOption('background', '#1a1a2e')
    pg.setConfigOption('foreground', '#e0e0e0')
except Exception as e:
    print(f"PyQtGraph 설정 오류: {e}")
    # 기본 설정으로 계속 진행


class CandlestickItem(pg.GraphicsObject):
    """캔들스틱 아이템"""

    def __init__(self):
        super().__init__()
        self.data = None
        self.bounds = [0, 0, 0, 0]  # [x_min, x_max, y_min, y_max]

    def setData(self, data):
        """데이터 설정

        Args:
            data: list of dicts with keys: timestamp, open, high, low, close
        """
        self.data = data
        self.updateBounds()
        self.update()

    def updateBounds(self):
        """데이터 경계 업데이트"""
        if not self.data:
            return

        timestamps = [d['timestamp'] for d in self.data]
        highs = [d['high'] for d in self.data]
        lows = [d['low'] for d in self.data]

        if timestamps and highs and lows:
            self.bounds = [min(timestamps), max(timestamps), min(lows), max(highs)]

    def boundingRect(self):
        """아이템 경계 반환"""
        return QRectF(*self.bounds)

    def paint(self, painter, option, widget=None):
        """캔들 그리기"""
        if not self.data:
            return

        painter.setRenderHint(QPainter.Antialiasing, False)

        # 데이터 포인트 수에 따라 선 두께 조정
        width = max(1, min(10, 6000 // len(self.data))) if self.data else 1

        for candle in self.data:
            x = candle['timestamp']
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            close_price = candle['close']

            # 색상 결정 (상승: 녹색, 하락: 빨강)
            if close_price >= open_price:
                color = QColor(0, 255, 159)  # 상승 - 녹색
            else:
                color = QColor(255, 71, 87)  # 하락 - 빨강

            painter.setPen(QPen(color, 0.5))

            # 고가-저가 선 그리기
            high_low_line = QLineF(x, high_price, x, low_price)
            painter.drawLine(high_low_line)

            # 시가-종가 사각형 그리기
            if close_price >= open_price:  # 상승
                rect = QRectF(x - width/2, open_price, width, close_price - open_price)
                painter.fillRect(rect, color)
            else:  # 하락
                rect = QRectF(x - width/2, close_price, width, open_price - close_price)
                painter.fillRect(rect, color)
                # 하락 시는 외곽선만 그리기 (속 비우기)
                painter.drawRect(rect)


class VolumeItem(pg.GraphicsObject):
    """거래량 아이템"""

    def __init__(self):
        super().__init__()
        self.data = None
        self.bounds = [0, 0, 0, 0]

    def setData(self, data):
        """데이터 설정"""
        self.data = data
        self.updateBounds()
        self.update()

    def updateBounds(self):
        """데이터 경계 업데이트"""
        if not self.data:
            return

        timestamps = [d['timestamp'] for d in self.data]
        volumes = [d['volume'] for d in self.data]

        if timestamps and volumes:
            self.bounds = [min(timestamps), max(timestamps), 0, max(volumes)]

    def boundingRect(self):
        """아이템 경계 반환"""
        return QRectF(*self.bounds)

    def paint(self, painter, option, widget=None):
        """거래량 막대 그리기"""
        if not self.data:
            return

        width = max(1, min(10, 6000 // len(self.data))) if self.data else 1

        for candle in self.data:
            x = candle['timestamp']
            volume = candle['volume']
            close_price = candle['close']
            open_price = candle['open']

            # 색상 결정
            if close_price >= open_price:
                color = QColor(0, 255, 159)  # 상승 - 녹색
            else:
                color = QColor(255, 71, 87)  # 하락 - 빨강

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 0.5))

            # 거래량 막대 그리기
            rect = QRectF(x - width/2, 0, width, volume)
            painter.drawRect(rect)


class LineIndicatorItem(pg.PlotDataItem):
    """라인 보조지표 아이템 (MA20 등)"""

    def __init__(self, name="Indicator", color='yellow', width=2):
        super().__init__()
        self.name = name
        self.setPen(pg.mkPen(color, width=width))


class CandlestickChartWidget(QWidget):
    """캔들 차트 위젯 - PyQtGraph 버전"""

    def __init__(self):
        super().__init__()
        self.current_data = None
        self.indicators_data = None
        self.timeframe = "1h"  # 기본 타임프레임
        self.exchange_id = ""
        self.symbol = ""
        self.data_loader_callback = None  # 동적 데이터 로딩 콜백

        try:
            self.setup_ui()
        except Exception as e:
            print(f"차트 위젯 초기화 오류: {e}")
            # 최소한의 UI만 생성
            layout = QVBoxLayout(self)
            error_label = QLabel("차트를 표시할 수 없습니다")
            error_label.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(error_label)

    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout(self)

        # 차트 제목 및 컨트롤
        control_layout = QHBoxLayout()

        self.title_label = QLabel("차트")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px; color: #e0e0e0;")

        try:
            self.chart_type = QComboBox()
            self.chart_type.addItems(["캔들 차트", "라인 차트", "거래량"])
            self.chart_type.currentTextChanged.connect(self.update_chart_type)

            self.indicator_toggle = QComboBox()
            self.indicator_toggle.addItems(["보조지표 없음", "MA20", "RSI", "MACD"])
            self.indicator_toggle.currentTextChanged.connect(self.update_chart)

            control_layout.addWidget(self.title_label)
            control_layout.addStretch()
            control_layout.addWidget(QLabel("차트 타입:"))
            control_layout.addWidget(self.chart_type)
            control_layout.addWidget(QLabel("보조지표:"))
            control_layout.addWidget(self.indicator_toggle)

            layout.addLayout(control_layout)

            # 차트 위젯 생성
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground('#1a1a2e')
            self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

            # 축 설정
            self.plot_widget.setLabel('left', '가격', color='#e0e0e0')
            self.plot_widget.setLabel('bottom', '시간', color='#e0e0e0')
            self.plot_widget.getAxis('left').setPen('#e0e0e0')
            self.plot_widget.getAxis('bottom').setPen('#e0e0e0')

            # 시간 축 포맷터 설정
            self.time_axis = pg.DateAxisItem()
            self.plot_widget.setAxisItems({'bottom': self.time_axis})

            # 뷰박스 설정 (확대/축소 가능)
            self.plot_widget.enableAutoRange()

            # 뷰 변경 감지를 위한 시그널 연결
            self.plot_widget.getViewBox().sigRangeChanged.connect(self._on_view_range_changed)

            # 아이템 초기화
            self.candlestick_item = CandlestickItem()
            self.volume_item = VolumeItem()
            self.ma20_item = LineIndicatorItem("MA20", '#ffd700', 2)
            self.rsi_item = LineIndicatorItem("RSI", '#ff6b6b', 1)
            self.macd_item = LineIndicatorItem("MACD", '#4ecdc4', 1)

            layout.addWidget(self.plot_widget)

        except Exception as e:
            print(f"차트 UI 생성 오류: {e}")
            # 기본 UI 생성
            error_label = QLabel("차트 로드 중 오류 발생")
            error_label.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(error_label)

    def update_chart_type(self, chart_type):
        """차트 타입 업데이트"""
        if self.current_data is not None:
            self.update_chart()

    def load_data(self, candles_data: list, indicators_data: dict = None, timeframe: str = None,
                 exchange_id: str = None, symbol: str = None):
        """
        차트 데이터 로드

        Args:
            candles_data: 캔들 데이터 리스트
            indicators_data: 보조지표 데이터 딕셔너리
            timeframe: 타임프레임
            exchange_id: 거래소 ID
            symbol: 심볼
        """
        if not candles_data:
            self.show_no_data_message()
            return

        try:
            # 차트 정보 저장
            if exchange_id:
                self.exchange_id = exchange_id
            if symbol:
                self.symbol = symbol
            if timeframe:
                self.timeframe = timeframe

            # timestamp를 Unix 타임스탬프(초)로 변환 (PyQtGraph DateAxisItem은 초 단위를 사용)
            for candle in candles_data:
                if isinstance(candle['timestamp'], str):
                    # 문자열인 경우 datetime으로 변환 후 타임스탬프로
                    dt = datetime.fromisoformat(candle['timestamp'])
                    candle['timestamp'] = dt.timestamp()
                elif isinstance(candle['timestamp'], (int, float)):
                    if candle['timestamp'] > 1e12:  # 밀리초 단위인 경우 초 단위로 변환
                        candle['timestamp'] = candle['timestamp'] / 1000

            # 데이터 정렬 (시간순)
            candles_data.sort(key=lambda x: x['timestamp'])

            self.current_data = candles_data
            self.indicators_data = indicators_data

            # 차트 업데이트
            self.update_chart()

        except Exception as e:
            print(f"차트 데이터 로드 실패: {str(e)}")
            self.show_error_message(str(e))

    def _get_time_format(self, timeframe):
        """타임프레임에 따른 시간 포맷 반환"""
        timeframe_formats = {
            "1m": "%m-%d %H:%M",
            "5m": "%m-%d %H:%M",
            "15m": "%m-%d %H:%M",
            "1h": "%m-%d %H:%M",
            "4h": "%m-%d %H:%M",
            "1d": "%Y-%m-%d"
        }
        return timeframe_formats.get(timeframe, "%m-%d %H:%M")

    def update_chart(self):
        """차트 업데이트"""
        if self.current_data is None or len(self.current_data) == 0:
            self.show_no_data_message()
            return

        try:
            # 차트 클리어
            self.plot_widget.clear()

            chart_type = self.chart_type.currentText()
            indicator = self.indicator_toggle.currentText()

            if chart_type == "캔들 차트":
                self.draw_candlestick_chart(indicator)
            elif chart_type == "라인 차트":
                self.draw_line_chart(indicator)
            elif chart_type == "거래량":
                self.draw_volume_chart()

            # 자동 범위 업데이트
            self.plot_widget.autoRange()

        except Exception as e:
            print(f"차트 업데이트 실패: {str(e)}")
            self.show_error_message(str(e))

    def draw_candlestick_chart(self, indicator: str):
        """캔들 차트 그리기"""
        # 커스텀 캔들 아이템 사용
        self.candlestick_item.setData(self.current_data)
        self.plot_widget.addItem(self.candlestick_item)

        # 보조지표 추가
        if indicator == "MA20" and self.indicators_data:
            self.add_ma20_indicator()
        elif indicator == "RSI" and self.indicators_data:
            # RSI는 별도 패널 대신 같은 패널에 표시 (0-100 범위)
            self.add_rsi_indicator()
        elif indicator == "MACD" and self.indicators_data:
            self.add_macd_indicator()

    def draw_line_chart(self, indicator: str):
        """라인 차트 그리기"""
        # 종가 라인
        timestamps = [candle['timestamp'] for candle in self.current_data]
        closes = [candle['close'] for candle in self.current_data]

        # PlotDataItem을 직접 사용하여 렌더링
        line_item = pg.PlotDataItem(
            x=timestamps,
            y=closes,
            pen=pg.mkPen('#00d4ff', width=2),
            name='Close',
            symbol=None,
            symbolSize=0,
            symbolBrush=None,
            symbolPen=None
        )
        self.plot_widget.addItem(line_item)

        # MA20 추가
        if indicator == "MA20" and self.indicators_data:
            self.add_ma20_indicator()

    def draw_volume_chart(self):
        """거래량 차트 그리기"""
        # 거래량은 캔들 차트와 함께 표시
        self.candlestick_item.setData(self.current_data)
        self.plot_widget.addItem(self.candlestick_item)

        self.volume_item.setData(self.current_data)

        # 거래량을 위한 두 번째 뷰 추가
        volume_view = pg.ViewBox()
        self.plot_widget.scene().addItem(volume_view)
        self.plot_widget.getAxis('right').linkToView(volume_view)
        volume_view.setXLink(self.plot_widget)

        volume_view.addItem(self.volume_item)
        volume_view.setBackgroundColor('#1a1a2e')

        # 오른쪽 축 라벨 설정
        self.plot_widget.getAxis('right').setLabel('거래량', color='#e0e0e0')
        self.plot_widget.getAxis('right').setPen('#e0e0e0')

    def add_ma20_indicator(self):
        """MA20 보조지표 추가"""
        ma20_values = []
        timestamps = []

        for candle in self.current_data:
            ts = int(candle['timestamp'])
            ts_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            indicator_data = self.indicators_data.get(ts_str) or self.indicators_data.get(ts * 1000, {})
            ma20 = indicator_data.get('ma_20')

            if ma20 is not None:
                ma20_values.append(float(ma20))
                timestamps.append(candle['timestamp'])

        if ma20_values:
            self.plot_widget.plot(timestamps, ma20_values, pen=pg.mkPen('#ffd700', width=2), name='MA20')

    def add_rsi_indicator(self):
        """RSI 보조지표 추가"""
        rsi_values = []
        timestamps = []

        for candle in self.current_data:
            ts = int(candle['timestamp'])
            ts_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            indicator_data = self.indicators_data.get(ts_str) or self.indicators_data.get(ts * 1000, {})
            rsi = indicator_data.get('rsi')

            if rsi is not None:
                rsi_values.append(float(rsi))
                timestamps.append(candle['timestamp'])

        if rsi_values:
            # RSI를 위한 두 번째 축 추가
            rsi_view = pg.ViewBox()
            self.plot_widget.scene().addItem(rsi_view)
            rsi_axis = pg.AxisItem('right')
            self.plot_widget.layout.addItem(rsi_axis, 2, 3)
            rsi_axis.linkToView(rsi_view)
            rsi_view.setXLink(self.plot_widget)

            rsi_view.plot(timestamps, rsi_values, pen=pg.mkPen('#ff6b6b', width=1), name='RSI')

            # RSI 레벨 라인 추가
            rsi_view.addLine(y=70, pen=pg.mkPen('#ff4757', style=2, width=1))  # 과매도
            rsi_view.addLine(y=30, pen=pg.mkPen('#00ff9f', style=2, width=1))  # 과매수

            rsi_axis.setLabel('RSI', color='#e0e0e0')
            rsi_axis.setPen('#e0e0e0')
            rsi_axis.setRange(0, 100)

    def add_macd_indicator(self):
        """MACD 보조지표 추가"""
        macd_values = []
        timestamps = []

        for candle in self.current_data:
            ts = int(candle['timestamp'])
            ts_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            indicator_data = self.indicators_data.get(ts_str) or self.indicators_data.get(ts * 1000, {})
            macd = indicator_data.get('macd')

            if macd is not None:
                macd_values.append(float(macd))
                timestamps.append(candle['timestamp'])

        if macd_values:
            # MACD를 위한 두 번째 축 추가
            macd_view = pg.ViewBox()
            self.plot_widget.scene().addItem(macd_view)
            macd_axis = pg.AxisItem('right')
            self.plot_widget.layout.addItem(macd_axis, 2, 3)
            macd_axis.linkToView(macd_view)
            macd_view.setXLink(self.plot_widget)

            macd_view.plot(timestamps, macd_values, pen=pg.mkPen('#4ecdc4', width=1), name='MACD')
            macd_view.addLine(y=0, pen=pg.mkPen('#e0e0e0', width=1))  # 0선

            macd_axis.setLabel('MACD', color='#e0e0e0')
            macd_axis.setPen('#e0e0e0')

    def show_no_data_message(self):
        """데이터 없음 메시지 표시"""
        self.plot_widget.clear()
        self.plot_widget.addItem(pg.TextItem("표시할 데이터가 없습니다\n거래소, 심볼, 타임프레임을 선택하고 데이터를 조회하세요",
                                          color='gray', anchor=(0.5, 0.5)))

    def show_error_message(self, error_msg: str):
        """에러 메시지 표시"""
        self.plot_widget.clear()
        self.plot_widget.addItem(pg.TextItem(f"차트 표시 오류:\n{error_msg}",
                                          color='red', anchor=(0.5, 0.5)))

    def clear_chart(self):
        """차트 클리어"""
        self.current_data = None
        self.indicators_data = None
        self.show_no_data_message()

    def _on_view_range_changed(self, view_box, new_range):
        """뷰 범위 변경 시 동적 데이터 로딩"""
        if not self.data_loader_callback or not self.exchange_id or not self.symbol:
            return

        try:
            # 현재 보이는 시간 범위
            x_min, x_max = new_range[0]

            # 현재 데이터의 시간 범위
            if self.current_data and len(self.current_data) > 0:
                current_min = min(candle['timestamp'] for candle in self.current_data)
                current_max = max(candle['timestamp'] for candle in self.current_data)

                # 왼쪽으로 확장해서 과거 데이터가 필요한 경우
                if x_min < current_min:
                    print(f"과거 데이터 요청: {datetime.fromtimestamp(x_min)} ~ {datetime.fromtimestamp(current_min)}")
                    # 콜백을 통해 추가 데이터 요청
                    if self.data_loader_callback:
                        self.data_loader_callback(
                            self.exchange_id,
                            self.symbol,
                            self.timeframe,
                            x_min,  # 시작 시간
                            current_min  # 종료 시간 (현재 데이터 시작 전까지)
                        )

        except Exception as e:
            print(f"동적 데이터 로딩 오류: {str(e)}")

    def set_data_loader_callback(self, callback):
        """데이터 로딩 콜백 설정"""
        self.data_loader_callback = callback

    def add_additional_data(self, new_data, new_indicators):
        """추가 데이터를 기존 데이터에 병합"""
        if not new_data:
            return

        try:
            # 타임스탬프 변환
            for candle in new_data:
                if isinstance(candle['timestamp'], str):
                    dt = datetime.fromisoformat(candle['timestamp'])
                    candle['timestamp'] = dt.timestamp()
                elif isinstance(candle['timestamp'], (int, float)):
                    if candle['timestamp'] > 1e12:
                        candle['timestamp'] = candle['timestamp'] / 1000

            # 기존 데이터와 병합
            self.current_data.extend(new_data)

            # 중복 제거 및 정렬
            seen = set()
            unique_data = []
            for candle in self.current_data:
                ts_key = candle['timestamp']
                if ts_key not in seen:
                    seen.add(ts_key)
                    unique_data.append(candle)

            self.current_data = sorted(unique_data, key=lambda x: x['timestamp'])

            # 보조지표 병합
            if new_indicators:
                self.indicators_data.update(new_indicators)

            # 차트 업데이트
            self.update_chart()

            print(f"추가 데이터 병합 완료: {len(new_data)}개 캔들")

        except Exception as e:
            print(f"데이터 병합 실패: {str(e)}")

    def set_title(self, title: str):
        """차트 제목 설정"""
        self.title_label.setText(title)