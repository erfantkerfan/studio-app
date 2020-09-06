import shutil
from datetime import timedelta

import pyscreenshot as ImageGrab
from timeloop import Timeloop

tl = Timeloop()
image = 'monitor' + '.png'
test = 'monitor' + '.test' + '.png'


@tl.job(interval=timedelta(seconds=2))
def grab_image():
    try:
        im = ImageGrab.grab()
        im.save(test)
        shutil.move(test, image)
    except:
        pass


if __name__ == "__main__":
    tl.start(block=True)
