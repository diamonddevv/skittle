from _ctx import skittle

if __name__ == "__main__":
    skittle.init()

    wnd = skittle.window.Window("hello, world!", 500, 500)
    wnd.run()