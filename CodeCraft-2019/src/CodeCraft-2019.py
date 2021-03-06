import logging
import sys
import processing

logging.basicConfig(level=logging.DEBUG,
                    filename='../logs/CodeCraft-2019.log',
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


def main():
    # config ="./1-map-training-1/"
    # config ="./1-map-training-2/"
    # config ="./1-map-training-3/"
    # config ="./1-map-training-4/"
    # config ="./1-map-exam-1/"
    config ="./1-map-exam-2/"
    # config ="./config/"
    car_path = config+"car.txt"
    road_path = config+"road.txt"
    cross_path = config+"cross.txt"
    answer_path = config+"answer.txt"
    temp_path = config+"temp.txt"
    if False:
        if len(sys.argv) != 5:
            logging.info(
                'please input args: car_path, road_path, cross_path, answerPath')
            exit(1)

        car_path = sys.argv[1]
        road_path = sys.argv[2]
        cross_path = sys.argv[3]
        answer_path = sys.argv[4]

    # logging.info("car_path is %s" % (car_path))
    # logging.info("road_path is %s" % (road_path))
    # logging.info("cross_path is %s" % (cross_path))
    # logging.info("answer_path is %s" % (answer_path))

    processing.Process(car_path, road_path, cross_path, answer_path,temp_path) 



if __name__ == "__main__":
    main()
