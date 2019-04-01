from tkinter import *
from tkinter import ttk, colorchooser, filedialog
from PIL import Image, ImageDraw
import math
import predict
import time, threading
import os
from threading import Thread, Event, Timer

#import PIL
#from PIL import ImageGrab

# def TimerReset(*args, **kwargs):
#     return _TimerReset(*args, **kwargs)
#
# class _TimerReset(Thread):
#     def __init__(self, interval, function, args=[], kwargs={}):
#         Thread.__init__(self)
#         self.interval = interval
#         self.function = function
#         self.args = args
#         self.kwargs = kwargs
#         self.finished = Event()
#         self.resetted = True
#
#     def cancel(self):
#         self.finished.set()
#
#     def run(self):
#         while self.resetted:
#             self.resetted = False
#             self.finished.wait(self.interval)
#
#         if not self.finished.isSet():
#             self.function(*self.args, **self.kwargs)
#         self.finished.set()
#
#     def reset(self, interval=None):
#         if interval:
#             self.interval = interval
#
#         self.resetted = True
#         self.finished.set()
#         self.finished.clear()


class main:
    def __init__(self, master):
        self.master = master
        self.color_fg = 'black'
        self.color_bg = 'white'
        self.old_x = None
        self.old_y = None
        self.left_most = None
        self.right_most = None
        self.top_most = None
        self.bottom_most = None
        self.canvas_width = 800
        self.canvas_height = 800
        self.penwidth = 3
        self.padding = 30
        self.drawWidgets()
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.image1 = Image.new("RGB", (self.canvas_width, self.canvas_height), self.color_bg)
        self.draw = ImageDraw.Draw(self.image1)
        self.timer = threading.Timer(2.5, self.classify)
        # self.timer = TimerReset(100, self.classify)
        self.count = 0
        self.point_list = []
        self.s = []
        self.lastLine = [];
        self.writing_mode = True;
        self.save_name = None
        self.save_count = 0
        self.scalar = 100.0

    class XYPair:
        def __init__(self, newx, newy):
            self.x = newx
            self.y = newy

    def paint(self, e):
        self.count = self.count + 1
        if self.count % 5 == 0:
            self.point_list.append(e)
        self.timer.cancel()
        if self.left_most is None:
            self.left_most = e.x

        if self.right_most is None:
            self.right_most = e.x

        if self.top_most is None:
            self.top_most = e.y

        if self.bottom_most is None:
            self.bottom_most = e.y

        if self.old_x and self.old_y:
            self.lastLine.append(self.c.create_line(self.old_x, self.old_y, e.x, e.y, width=self.penwidth, fill=self.color_fg, capstyle = ROUND, smooth = True))
            self.draw.line((self.old_x, self.old_y, e.x, e.y), fill=(0,0,0), width=self.penwidth)

        if e.x < self.left_most:
            self.left_most = e.x

        if e.y < self.top_most:
            self.top_most = e.y

        if e.x > self.right_most:
            self.right_most = e.x

        if e.y > self.bottom_most:
            self.bottom_most = e.y

        self.old_x = e.x
        self.old_y = e.y


    def reset(self, e):
        self.old_x = None
        self.old_y = None
        self.lineSmooth()
        self.s.clear()
        self.point_list.clear()
        self.point_list.clear()
        self.lastLine.clear();
        #self.timer = TimerReset(100, self.classify(self.image1))
        if self.writing_mode is True:
            self.timer = threading.Timer(1.5, self.classify)
            self.timer.start()

    def lineSmooth(self):
        pix = []
        piy = []
        d = []
        self.s.append(self.point_list[0]);
        self.s.append(self.point_list[1]);
        for i in range(2, len(self.point_list)-2):
            d.clear()
            d.append(self.scalar*math.sqrt(pow(abs(self.point_list[i].x - self.point_list[i-2].x), 2) + pow(abs(self.point_list[i].y - self.point_list[i - 2].y), 2)))
            d.append(self.scalar*math.sqrt(pow(abs(self.point_list[i].x - self.point_list[i-1].x), 2) + pow(abs(self.point_list[i].y - self.point_list[i - 1].y), 2)))
            d.append(self.scalar*math.sqrt(pow(abs(self.point_list[i].x - self.point_list[i+1].x), 2) + pow(abs(self.point_list[i].y - self.point_list[i + 1].y), 2)))
            d.append(self.scalar*math.sqrt(pow(abs(self.point_list[i].x - self.point_list[i+2].x), 2) + pow(abs(self.point_list[i].y - self.point_list[i + 2].y), 2)))

            pix.append((self.point_list[i - 2].x/d[0] + self.point_list[i - 1].x/d[1] + self.point_list[i + 1].x/d[2] + self.point_list[i + 2].x/d[3])/(1/d[0] + 1/d[1] + 1/d[2] + 1/d[3]))
            piy.append((self.point_list[i - 2].y/d[0] + self.point_list[i - 1].y/d[1] + self.point_list[i + 1].y/d[2] + self.point_list[i + 2].y/d[3])/(1/d[0] + 1/d[1] + 1/d[2] + 1/d[3]))

            coord = self.XYPair(pix[i - 2], piy[i-2])

            self.s.append(coord)
        for i in range(0, len(self.lastLine)):
            self.c.delete(self.lastLine[i])
        self.s.append(self.point_list[len(self.point_list)-2])
        self.s.append(self.point_list[len(self.point_list) - 1])
        for i in range(0, len(self.s)):
            self.paint(self.s[i])
        self.s.clear();
        self.old_x = None
        self.old_y = None



    def classify(self, img = None):
        if img is None:
            img = self.image1
        self.save()
        text = predict.predict(self.save_name)
        self.T.insert(END, text)
        self.T.insert(END, " ")
        path = 'C:/Users/Jesse Jensen/Desktop/MNIST_data/' + 'Number' + str(self.save_count) + '.png'
        os.remove(path)

        #return text

        print('classifying...')
        #self.T.insert(END, predict.predict(img))
        #print("hi")

    def changeW(self, e):
        self.penwidth = int(float(e))

    def save(self):
        self.save_count = self.save_count+1
        #file = filedialog.asksaveasfilename(filetypes=[('.png', '*.png')])
        #if file:
            # x = self.master.winfo_rootx() + self.c.winfo_x() + self.left_most   #self.c.winfo_x()
            # y = self.master.winfo_rooty() + self.c.winfo_y() + self.top_most #self.c.winfo_y()
            #
            # x1 = x + (self.right_most - self.left_most) #self.c.winfo_width()
            # y1 = y + (self.bottom_most - self.top_most) #self.c.winfo_height()

        x = self.left_most - self.padding
        y = self.top_most - self.padding
        x1 = self.right_most + self.padding
        y1 = self.bottom_most + self.padding
            #PIL.ImageGrab.grab().crop((x, y, x1, y1)).save(file + '.png')
            #PIL.ImageGrab.grab(bbox=(x, y, x1, y1)).save(file + '.png')

        self.image1.crop((x, y, x1, y1)).save('Number' + str(self.save_count) + '.png')
        self.save_name = ('Number' + str(self.save_count) + '.png')


    def clear(self):
        self.c.delete(ALL)
        self.left_most = None
        self.right_most = None
        self.top_most = None
        self.bottom_most = None
        self.image1.close()
        self.image1 = Image.new("RGB", (self.canvas_width, self.canvas_height), self.color_bg)
        self.draw = ImageDraw.Draw(self.image1)

    def change_fg(self):
        self.color_fg = colorchooser.askcolor(color=self.color_fg)[1]
        self.c['fg'] = self.color_fg

    def change_bg(self):
        self.color_bg=colorchooser.askcolor(color=self.color_bg)[1]
        self.c['bg'] = self.color_bg

    def setWritingMode(self):
        self.writing_mode = True

    def cancelWritingMode(self):
        self.writing_mode = False

    def drawWidgets(self):
        self.controls = Frame(self.master, padx = 5, pady = 5)
        Label(self.controls, text='Pen Width: ', font=(",15")).grid(row=0, column=0)
        self.slider = ttk.Scale(self.controls, from_=1, to=100, command=self.changeW, orient=HORIZONTAL)
        self.slider.set(self.penwidth)
        self.slider.grid(row=0, column =1, ipadx = 30)
        #self.controls.pack()

        self.T = Text(self.master, height=2, width=30)
        #self.T.grid(row=0, column=0)
        self.T.pack(side=TOP)

        self.button1 = Button(self.master, text="Writing Mode", command=self.setWritingMode)
        #self.button1.grid(row=0, column=2)
        self.button1.pack()

        self.button2 = Button(self.master, text="Drawing Mode", command=self.cancelWritingMode)
        #self.button2.grid(row=1, column = 2)
        self.button2.pack()

        self.button3 = Button(self.master, text="Clear", command=self.clear)
        #self.button3.grid(row=0, column=1)
        self.button3.pack()

        self.c = Canvas(self.master, width = self.canvas_width, height = self.canvas_height, bg = self.color_bg,)
        #self.c.grid(fill=BOTH, expand=True)
        self.c.pack(fill=BOTH, expand=True)

        menu = Menu(self.master)
        self.master.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='File',menu=filemenu)
        filemenu.add_command(label='Export',command=self.save)
        colormenu = Menu(menu)
        menu.add_cascade(label='Colors', menu=colormenu)
        colormenu.add_command(label='Brush Color', command=self.change_fg)
        colormenu.add_command(label='Background Color', command=self.change_bg)
        optionmenu = Menu(menu)
        menu.add_cascade(label='Options', menu=optionmenu)
        optionmenu.add_command(label='Clear', command=self.clear)
        optionmenu.add_command(label='Exit', command=self.master.destroy)


if __name__ == '__main__':
    root = Tk()
    main(root)
    root.title('DrawGUI')
    root.mainloop()
