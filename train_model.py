from model import *

x_train, x_test, y_train, y_test = parse_csv()
build(x_train, x_test, y_train, y_test)