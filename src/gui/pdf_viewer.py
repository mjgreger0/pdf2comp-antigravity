import fitz  # PyMuPDF
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QSizePolicy, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt, QRectF, Signal

class PdfPageWidget(QLabel):
    """
    Widget to display a single page of a PDF.
    Supports drawing highlight rectangles.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._image = None
        self._highlights = []  # List of (rect, color) tuples. rect is normalized (0-1)
        self._scale = 1.0

    def set_page_image(self, pixmap: QPixmap, scale: float):
        self._image = pixmap
        self._scale = scale
        self.setPixmap(self._image)

    def set_highlights(self, highlights):
        """
        Set the list of highlights to draw.
        :param highlights: List of tuples (rect, color). 
                           rect is (x0, y0, x1, y1) normalized coordinates.
                           color is QColor.
        """
        self._highlights = highlights
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._image or not self._highlights:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        for rect_norm, color in self._highlights:
            # Convert normalized coordinates to pixel coordinates
            x0, y0, x1, y1 = rect_norm
            rect = QRectF(
                x0 * width,
                y0 * height,
                (x1 - x0) * width,
                (y1 - y0) * height
            )
            
            # Draw highlight
            brush = QBrush(color)
            painter.setBrush(brush)
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)
            
            # Optional: Draw border
            pen = QPen(color.darker(150))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRect(rect)

class PdfViewer(QWidget):
    """
    Main PDF Viewer widget containing a scroll area and page display.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Control Bar
        self.control_layout = QHBoxLayout()
        self.btn_prev = QPushButton("Previous")
        self.btn_next = QPushButton("Next")
        self.lbl_page = QLabel("Page: 0 / 0")
        self.btn_zoom_in = QPushButton("Zoom In")
        self.btn_zoom_out = QPushButton("Zoom Out")

        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)

        self.control_layout.addWidget(self.btn_prev)
        self.control_layout.addWidget(self.lbl_page)
        self.control_layout.addWidget(self.btn_next)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.btn_zoom_out)
        self.control_layout.addWidget(self.btn_zoom_in)

        self.layout.addLayout(self.control_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Container for pages (currently single page for simplicity, can be expanded)
        self.page_container = QWidget()
        self.page_layout = QVBoxLayout(self.page_container)
        self.page_layout.setContentsMargins(10, 10, 10, 10)
        self.page_layout.setSpacing(10)
        
        self.page_widget = PdfPageWidget()
        self.page_layout.addWidget(self.page_widget)
        self.page_layout.addStretch()
        
        self.scroll_area.setWidget(self.page_container)
        self.layout.addWidget(self.scroll_area)

        self.doc = None
        self.current_page_index = 0
        self.zoom_level = 1.0

    def load_document(self, file_path):
        try:
            self.doc = fitz.open(file_path)
            self.current_page_index = 0
            self.render_page()
            self.update_controls()
        except Exception as e:
            print(f"Error loading PDF: {e}")

    def render_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.current_page_index)
        
        # Calculate matrix for zoom
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to QImage
        img_format = QImage.Format_RGB888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
        
        # Convert to QPixmap
        pixmap = QPixmap.fromImage(img)
        
        self.page_widget.set_page_image(pixmap, self.zoom_level)

    def update_controls(self):
        if not self.doc:
            self.lbl_page.setText("Page: 0 / 0")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return
        
        total_pages = len(self.doc)
        self.lbl_page.setText(f"Page: {self.current_page_index + 1} / {total_pages}")
        self.btn_prev.setEnabled(self.current_page_index > 0)
        self.btn_next.setEnabled(self.current_page_index < total_pages - 1)

    def prev_page(self):
        if self.doc and self.current_page_index > 0:
            self.current_page_index -= 1
            self.render_page()
            self.update_controls()

    def next_page(self):
        if self.doc and self.current_page_index < len(self.doc) - 1:
            self.current_page_index += 1
            self.render_page()
            self.update_controls()

    def highlight_rects(self, rects, page_num=0):
        """
        Highlight specific rectangles on a page.
        :param rects: List of (x0, y0, x1, y1) normalized coordinates.
        :param page_num: Page number to highlight.
        """
        if page_num != self.current_page_index:
            self.current_page_index = page_num
            self.render_page()
            self.update_controls()
            
        highlights = [(r, QColor(255, 255, 0, 100)) for r in rects] # Yellow, semi-transparent
        self.page_widget.set_highlights(highlights)

    def clear_highlights(self):
        self.page_widget.set_highlights([])

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.render_page()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.render_page()
