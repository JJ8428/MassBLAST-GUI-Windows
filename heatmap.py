from PIL import Image as IMG
from PIL import ImageDraw, ImageFont
import random, math
from tkinter import *
from custom_tk import *
import threading

''' Draw the heatmap without any axes '''
def heatmap(col_heading, row_heading, data, scale="linear", reverse=False):

    width = 40 * col_heading.__len__()
    height = 20 * row_heading.__len__()
    im = IMG.new("RGB", (width, height), (80, 80, 80))
    draw = ImageDraw.Draw(im)
    labelling = ImageFont.truetype("resources/arial.ttf", 10)
    max = data[0][0]
    for a in range(0, data.__len__()):
        for b in range(0, data[0].__len__()):
            if data[a][b] > max:
                max = data[a][b]
    if max == 0:
        max = 1
    for a in range(0, data.__len__()):
        for b in range(0, data[0].__len__()):
            left =  40*b
            right = left + 40
            top = 20*a
            bottom = top + 20
            if data[a][b] == -1: # No hit
                draw.rectangle((left, top, right, bottom), fill=(255, 0, 0), outline=(255, 0, 0))
            elif data[a][b] == -2: # Filtered out
                draw.rectangle((left, top, right, bottom), fill=(0, 0, 255), outline=(0, 0, 255))
            else:
                rating = data[a][b] / max
                if reverse: # Reverse is to be only called on when mapping the gap, since a lower gap is better, requiring a greener rgb value
                    rating = 1 - rating
                if scale == "quadratic":
                    gr = (rating) ** 2
                elif scale == "linear":
                    gr = rating
                elif scale == "logarithmic":
                    if rating != 0:
                        gr = math.log(rating+1, 2)
                    else:
                        gr = 0
                gr = int(gr * 255)
                draw.rectangle((left, top, right, bottom), fill=(0, gr, 0), outline=(0, gr, 0))
                draw.text((left+2, top), str(data[a][b]), fill=(255, 255, 255, 255), font=labelling)
    for a in range(0, row_heading.__len__()):
        draw.line(((0, 20*a), (width, 20*a)), fill=(255, 255, 255, 255), width=0)
    draw.line(((0, 20), (width, 20)), fill=(255, 255, 255, 255), width=0)
    for a in range(0, col_heading.__len__()):
        draw.line(((40*a, 0), (40*a, height)), fill=(255, 255, 255, 255), width=0)
    return im

''' Draw the x axis, only good for numercal x axes '''
def x_axis(col_heading):

    width = 40 * col_heading.__len__()
    height = 20 * 2
    im = IMG.new("RGB", (width, height), (80, 80, 80))
    draw = ImageDraw.Draw(im)
    labelling = ImageFont.truetype("resources/arial.ttf", 16)
    for a in range(0, col_heading.__len__()):
        if col_heading[a] % 5 == 0:
            draw.text(((40*a)+4, 0), str(col_heading[a]), fill=(255, 255, 255, 255), font=labelling)
            draw.line(((40*(a), 0), (40*(a), height)), fill=(255, 255, 255, 255), width=0)
        else:
            draw.line(((40*(a), 20), (40*(a), height)), fill=(255, 255, 255, 255), width=0)
    return im

''' 
Draws the y axis, but this is meant for categorical data 
This method can also be used to generate the x_axis with categorical data
Very useful for the correlation HM
'''
def y_axis(row_heading, _height = 20, x_axis = False):

    width = 250
    height = _height * row_heading.__len__()
    dim = (width, height)
    im = IMG.new("RGB", dim, (80, 80, 80))
    draw = ImageDraw.Draw(im)
    labelling = ImageFont.truetype("resources/arial.ttf", 16)
    for a in range(0, row_heading.__len__()):
        draw.text((4, _height*(a)+2), str(row_heading[a]), fill=(255, 255, 255, 255), font=labelling)
        draw.line(((0, _height*(a+1)+1), (width, _height*(a+1)+1)), fill=(255, 255, 255, 255), width=0)
    if x_axis: # Draw it as a x-axis
        im = im.transpose(IMG.ROTATE_90)
    return im

def gen_hxy(col_heading, row_heading, data, scale, save_as, reverse=False):

    def im_h():
        imh = heatmap(col_heading, row_heading, data, scale, reverse)
        imh.save("viewing/"+save_as+"-hm.png")

    def im_x():
        imx = x_axis(col_heading)
        imx.save("viewing/"+save_as+"-x.png")

    def im_y():
        imy = y_axis(row_heading)
        imy.save("viewing/"+save_as+"-y.png")

    spool = []
    t1 = threading.Thread(target=im_h)
    t1.start()
    spool.append(t1)
    t2 = threading.Thread(target=im_x)
    t2.start()
    spool.append(t2)
    t3 = threading.Thread(target=im_y)
    t3.start()
    spool.append(t3)
    for thread in spool:
        thread.join()

''' Same function as above, but instead using copy and paste '''
def gen_export(path, export_as):

    hm = IMG.open("viewing/"+path+"-hm.png")
    x_axis = IMG.open("viewing/"+path+"-x.png")
    y_axis = IMG.open("viewing/"+path+"-y.png")
    width = y_axis.size[0] + hm.size[0]
    height = x_axis.size[1] + hm.size[1]
    im = IMG.new("RGB", (width, height), (80, 80, 80))
    im.paste(hm, (250, 40))
    im.paste(x_axis, (250, 0))
    im.paste(y_axis, (0, 39))
    im.save(export_as)

''' Generates the x, y axes and the heatmap '''
def corr_gen_hxy(subjects, data, scale, path, reverse=False):

    y_axis(subjects).save("viewing/"+path+"-y.png")
    # Using the y_axis function to generate the categorical x_axis
    y_axis(subjects, 40, True).save("viewing/"+path+"-x.png") 
    heatmap(subjects, subjects, data, scale, reverse).save("viewing/"+path+"-hm.png")

''' gen_export, but for the correlation... Did I mention I am tired of this project? '''
def corr_gen_export(path, export_as):

    hm = IMG.open("viewing/"+path+"-hm.png")
    x_axis = IMG.open("viewing/"+path+"-x.png")
    y_axis = IMG.open("viewing/"+path+"-y.png")
    width = y_axis.size[0] + hm.size[0]
    height = x_axis.size[1] + hm.size[1]
    im = IMG.new("RGB", (width, height), (80, 80, 80))
    im.paste(hm, (250, 250))
    im.paste(x_axis, (250, 0))
    im.paste(y_axis, (0, 249))
    im.save(export_as)