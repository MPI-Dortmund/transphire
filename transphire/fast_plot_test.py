import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as plp
import numpy as np
import time


def scale_axis(ax, func, old_min, new_min, old_max, new_max, change):
    if old_min > new_min or old_max < new_max:
        if old_min > new_min:
            old_min = new_min - abs(new_min*0.1)
        if old_max < new_max:
            old_max = new_max + abs(new_max*0.1)
        func([old_min, old_max])
        change = True
    return old_min, old_max, change


def new():
    print('new')
    fig, ax = plt.subplots()
    y = np.random.randn(100)
    line, = ax.plot(y)
    old_y_min = min(y)
    old_y_max = max(y)
    old_x_min = 0
    old_x_max = len(y)
    fig.canvas.draw()
    plt.show(block=False)

    tstart = time.time()
    num_plots = 0
    while time.time()-tstart < 5:
        y = np.random.randn(100+num_plots*5)
        old_y_min, old_y_max, change = scale_axis(ax, ax.set_ylim, old_y_min, min(y), old_y_max, max(y), False)
        old_x_min, old_x_max, change = scale_axis(ax, ax.set_xlim, old_x_min, 0, old_x_max, len(y), change)
        if change:
            fig.canvas.draw()
        line.set_data([np.arange(len(y)), y])
        ax.draw_artist(ax.patch)
        ax.draw_artist(line)
        fig.canvas.update()
        fig.canvas.flush_events()
        num_plots += 1
    print(num_plots/5)

    fig, ax = plt.subplots()
    y, x = np.histogram(np.random.randn(100))
    rects = ax.bar(x[:-1], y, width=x[1]-x[0])
    old_y_min = min(y)
    old_y_max = max(y)
    old_x_min = min(x)
    old_x_max = max(x)

    fig.canvas.draw()
    plt.show(block=False)

    tstart = time.time()
    num_plots = 0
    while time.time()-tstart < 5:
        y, x = np.histogram(np.random.randn(100+num_plots*5))
        old_y_min, old_y_max, change = scale_axis(ax, ax.set_ylim, old_y_min, min(y), old_y_max, max(y), False)
        old_x_min, old_x_max, change = scale_axis(ax, ax.set_xlim, old_x_min, min(x), old_x_max, max(x), change)
        [rect.set_height(y1) for rect, y1 in zip(rects, y)]
        fig.canvas.draw()
        #fig.canvas.update()
        fig.canvas.flush_events()
        num_plots += 1
    print(num_plots/5)

    fig, ax = plt.subplots()
    values = np.random.randint(0, 255, 300).reshape(10, 10, 3)
    img = ax.imshow(values)

    plt.show(block=False)

    tstart = time.time()
    num_plots = 0
    while time.time()-tstart < 5:
        values = np.random.randint(0, 255, 300).reshape(10, 10, 3)
        img.set_data(values)
        fig.canvas.draw()
        #fig.canvas.update()
        fig.canvas.flush_events()
        num_plots += 1
    print(num_plots/5)


def old():
    print('old')
    fig, ax = plt.subplots()
    ax.plot(np.random.randn(100))
    plt.show(block=False)

    tstart = time.time()
    num_plots = 0
    while time.time()-tstart < 5:
        ax.clear()
        ax.plot(np.random.randn(100))
        fig.canvas.draw()
        fig.canvas.flush_events()
        num_plots += 1
    print(num_plots/5)

    fig, ax = plt.subplots()
    y, x = np.histogram(np.random.randn(100))
    ax.hist(y)
    plt.show(block=False)

    tstart = time.time()
    num_plots = 0
    while time.time()-tstart < 5:
        y, x = np.histogram(np.random.randn(100+num_plots*5))
        ax.clear()
        ax.hist(y)
        fig.canvas.draw()
        fig.canvas.flush_events()
        num_plots += 1
    print(num_plots/5)

    fig, ax = plt.subplots()
    values = np.random.randint(0, 255, 300).reshape(10, 10, 3)
    ax.imshow(values)

    plt.show(block=False)

    tstart = time.time()
    num_plots = 0
    while time.time()-tstart < 5:
        values = np.random.randint(0, 255, 300).reshape(10, 10, 3)
        ax.imshow(values)
        fig.canvas.draw()
        fig.canvas.flush_events()
        num_plots += 1
    print(num_plots/5)

new()
old()
