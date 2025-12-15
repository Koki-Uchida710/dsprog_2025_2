import flet as ft
import math


# --- ボタン定義 ---
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24  
        self.color = ft.Colors.WHITE     

class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE   
        self.color = ft.Colors.WHITE     

class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100 
        self.color = ft.Colors.BLACK           

class ScienceButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.TEAL     
        self.color = ft.Colors.WHITE      

# --- アプリ本体 ---

class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=30, text_align="right") # 修正
        self.width = 370 
        self.bgcolor = ft.Colors.BLACK    # 修正: colors -> Colors
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20

        # 科学計算用キーパッド（初期状態は非表示）
        self.sci_rows = ft.Column(
            visible=False,
            controls=[
                ft.Row(
                    controls=[
                        ScienceButton(text="sin", button_clicked=self.button_clicked),
                        ScienceButton(text="cos", button_clicked=self.button_clicked),
                        ScienceButton(text="tan", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ScienceButton(text="log", button_clicked=self.button_clicked),
                        ScienceButton(text="sqrt", button_clicked=self.button_clicked),
                        ScienceButton(text="^", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ScienceButton(text="π", button_clicked=self.button_clicked),
                        ScienceButton(text="(", button_clicked=self.button_clicked),
                        ScienceButton(text=")", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                
                # 科学計算エリア
                self.sci_rows,

                # 標準機能エリア
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="Sci", button_clicked=self.button_clicked), 
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")

        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
        
        elif data == "Sci":
            self.sci_rows.visible = not self.sci_rows.visible
            self.update()

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        elif data in ("+", "-", "*", "/", "^"):
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True

        elif data in ("="):
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.reset()

        elif data in ("%"):
            self.result.value = self.format_number(float(self.result.value) / 100)
            self.reset()
        
        elif data == "π":
            self.result.value = str(math.pi)
            self.new_operand = False

        elif data in ("sin", "cos", "tan", "log", "sqrt"):
            try:
                val = float(self.result.value)
                res = 0
                if data == "sin":
                    res = math.sin(val)
                elif data == "cos":
                    res = math.cos(val)
                elif data == "tan":
                    res = math.tan(val)
                elif data == "log":
                    if val <= 0: res = "Error"
                    else: res = math.log(val)
                elif data == "sqrt":
                    if val < 0: res = "Error"
                    else: res = math.sqrt(val)
                
                if res == "Error":
                    self.result.value = "Error"
                else:
                    self.result.value = self.format_number(res)
                
                self.new_operand = True 

            except Exception:
                self.result.value = "Error"

        elif data in ("+/-"):
            if float(self.result.value) > 0:
                self.result.value = "-" + str(self.result.value)
            elif float(self.result.value) < 0:
                self.result.value = str(self.format_number(abs(float(self.result.value))))

        self.update()

    def format_number(self, num):
        if isinstance(num, str): return num 
        if num % 1 == 0:
            return int(num)
        else:
            return round(num, 10)

    def calculate(self, operand1, operand2, operator):
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            elif operator == "-":
                return self.format_number(operand1 - operand2)
            elif operator == "*":
                return self.format_number(operand1 * operand2)
            elif operator == "/":
                if operand2 == 0:
                    return "Error"
                else:
                    return self.format_number(operand1 / operand2)
            elif operator == "^":
                return self.format_number(math.pow(operand1, operand2))
        except Exception:
            return "Error"
        return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Scientific Calculator"
    # 背景色もColorsクラスに変更
    page.bgcolor = ft.Colors.BLUE_GREY 
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    
    calc = CalculatorApp()
    page.add(calc)

if __name__ == "__main__":
    ft.app(target=main)