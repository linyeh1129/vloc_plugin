from importlib.util import find_spec
from dataclasses import dataclass
import re
import cv2
import pytesseract
from vloc.module import VlocModule
from vloc.exception import VlocOcrError
if find_spec('vloc.plugin.__selenium__'):
    from vloc.plugin.__selenium__.__info__ import DetectAction as SeleniumDetectAction


@dataclass
class DetectInfo:
    x: int
    y: int
    label: str
    conf: float
    crop: str
    ocr: str = None

    def __post_init__(self):

        if any(cls in str(VlocModule.screenshot_method.__self__) for cls in ['selenium', 'appium']):
            action = SeleniumDetectAction(self.x, self.y, VlocModule.screenshot_method.__self__)

            self.click = action.click
            self.input = action.input

    def click(self):
        ...

    def input(self, value: str):
        ...

    def text(self,
             search: re.Pattern = None,
             remove: re.Pattern = None,
             segment: bool = True) -> str:

        img = cv2.imread(self.crop)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        config = '--psm 4' if segment else '--psm 7'

        txt = str(pytesseract.image_to_string(img, config=config)).replace('\n', '')

        if search:
            txt = re.search(search, txt)
            if not txt:
                raise VlocOcrError(f'text search pattern not contains:{search}')
            txt = txt.group(0)

        txt = re.sub(remove, '', txt).strip() if remove else txt
        return txt
