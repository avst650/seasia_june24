import pyautogui
import time

j=1

while True:
    try:
        x,y=pyautogui.position()
        pyautogui.scroll(j)
        pyautogui.press('x')
        pyautogui.press('o')
        pyautogui.press('t')
        pyautogui.press('i')
        pyautogui.press('l')
        pyautogui.press('l')
        pyautogui.press('w')
        pyautogui.press('e')
        pyautogui.press('o')
        pyautogui.press('d')
        pyautogui.press(':')
        pyautogui.press(')')
                
        time.sleep(25)
        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')
        
        time.sleep(25)
        pyautogui.scroll(j)
        pyautogui.press('y')
        pyautogui.press('e')
        pyautogui.press('a')
        pyautogui.press('h')
        pyautogui.press('t')
        pyautogui.press('h')
        pyautogui.press('a')
        pyautogui.press('t')
        pyautogui.press('s')
        pyautogui.press('i')
        pyautogui.press('t')
        pyautogui.press('!')
        xx, yy=pyautogui.position()

    except:
        pass
        
