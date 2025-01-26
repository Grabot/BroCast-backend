import math
import os
import random
import stat

from PIL import Image, ImageDraw

angles = [83, 84, 85, 86, 94, 95, 96, 97]
min_line_length = 20
colours = [
    "#b44ac0",
    "#000000",
    "#009eaa",
    "#ffd635",
    "#00cc78",
    "#2450a4",
    "#6a5cff",
    "#7eed56",
    "#493ac1",
    "#00a368",
    "#d4d7d9",
    "#be0039",
    "#898d90",
    "#9c6926",
    "#3690ea",
    "#00756f",
    "#ff99aa",
    "#811e9f",
    "#6d482f",
    "#51e9f4",
    "#ff4500",
    "#ffa800",
    "#ffffff",
    "#ff3881",
]


class Line:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.next = None

    def set_next(self, line):
        self.next = line

    def get_next(self):
        return self.next

    def get_length(self):
        x_length = abs(self.start[0] - self.end[0])
        y_length = abs(self.start[1] - self.end[1])
        return math.sqrt(math.pow(x_length, 2) + math.pow(y_length, 2))


class Plane:
    def __init__(self, points, colour):
        self.points = points
        # The plane will always be a rectangle with 4 lines
        line1 = Line(points[0], points[1])
        line2 = Line(points[1], points[2])
        line3 = Line(points[2], points[3])
        line4 = Line(points[3], points[0])
        line1.set_next(line2)
        line2.set_next(line3)
        line3.set_next(line4)
        line4.set_next(line1)
        self.lines = [line1, line2, line3, line4]
        self.colour = colour

    def get_all_lines(self):
        return self.lines

    def get_line(self, line_choice):
        return self.lines[line_choice]

    def set_colour(self, colour):
        self.colour = colour

    def get_colour(self):
        return self.colour


def get_angle_lines(line_1, line_2):
    # https://stackoverflow.com/questions/28260962/calculating-angles-between-line-segments-python-with-math-atan2
    slope1 = slope_line(line_1.start, line_1.end)
    slope2 = slope_line(line_2.start, line_2.end)
    return angle_slopes(slope1, slope2)


def slope_line(point_1, point_2):
    dividend = point_2[1] - point_1[1]
    divisor = point_2[0] - point_1[0]
    return dividend / divisor


def angle_slopes(slope_1, slope_2):
    divisor = 1 + (slope_2 * slope_1)
    if divisor == 0:
        divisor = 0.00001
    ang_rad = math.atan((slope_2 - slope_1) / divisor)
    ang = math.degrees(ang_rad)
    # We know we have a convex quadrilateral
    # so all angles are positive and between 0 and 180
    if ang > 180:
        return ang - 180
    elif ang < -180:
        return ang + 360
    elif ang < 0:
        return ang + 180
    else:
        return ang


def point_on_line(_line, _point):
    segment_1 = Line(_line.start, _point)
    segment_2 = Line(_point, _line.end)

    segments_length = segment_1.get_length() + segment_2.get_length()
    # Damn floating points!
    if abs(_line.get_length() - segments_length) <= 0.001:
        return True
    else:
        return False


def point_on_plane(_plane, _point):
    line_1 = _plane.get_line(0)
    line_2 = _plane.get_line(1)
    line_3 = _plane.get_line(2)
    line_4 = _plane.get_line(3)
    # If the point is on any of the 4 lines of the plane it is fine.
    if (
        point_on_line(line_1, _point)
        or point_on_line(line_2, _point)
        or point_on_line(line_3, _point)
        or point_on_line(line_4, _point)
    ):
        return True
    else:
        return False


def get_length(start_point, end_point):
    x_length = abs(start_point[0] - end_point[0])
    y_length = abs(start_point[1] - end_point[1])
    return math.sqrt(math.pow(x_length, 2) + math.pow(y_length, 2))


def add_square_clean(_rand, _width, _height, _planes, _index):
    attempts = 0
    while attempts < 100:
        attempts += 1
        colour_index = _rand.randint(_index, len(colours) - 1 + _index)
        colour_index -= _index
        _index += 1

        plane_choice = _rand.randint(_index, len(_planes) - 1 + _index)
        plane_choice -= _index
        _index += 1
        # This is the square that we will want to divide in 2 squares!
        plane = _planes[plane_choice]

        line_choice = _rand.randint(_index, 3 + _index)
        line_choice -= _index
        _index += 1
        line = plane.get_line(line_choice)
        # It's possible that a line is shorter
        # than the minimum length because of the angles, don't pick these
        if line.get_length() <= min_line_length:
            continue
        next_line = line.get_next()
        # We are going to split the chosen line somewhere and attempt to
        # calculate the new resulting plane split using the chosen angle
        line_length_choice = _rand.uniform(_index + min_line_length, line.get_length() + _index)
        line_length_choice -= _index
        _index += 1

        angle_choice = _rand.randint(_index, len(angles) + _index)
        angle_choice -= _index
        angle_choice -= 1
        _index += 1

        ang_1 = angles[angle_choice]

        # Sin(a_1) = Opp/Hyp
        # First we don't know the angle, but we know the Opp and Hyp
        angle_1 = math.degrees(math.asin((line.end[1] - line.start[1]) / line.get_length()))

        # Sin(a_1) = Opp/Hyp
        # Now we know the angle and the Hyp
        test_point_a_1 = line.start
        opp = math.sin(math.radians(angle_1)) * line_length_choice
        adj = math.sqrt(math.pow(line_length_choice, 2) - math.pow(opp, 2))

        test_point_a_2 = [test_point_a_1[0] + adj, test_point_a_1[1] + opp]
        if not point_on_line(line, test_point_a_2):
            test_point_a_2 = [test_point_a_1[0] - adj, test_point_a_1[1] + opp]
        if not point_on_line(line, test_point_a_2):
            test_point_a_2 = [test_point_a_1[0] + adj, test_point_a_1[1] - opp]
        if not point_on_line(line, test_point_a_2):
            test_point_a_2 = [test_point_a_1[0] - adj, test_point_a_1[1] - opp]
        if not point_on_line(line, test_point_a_2):
            continue

        test_point_b_1 = test_point_a_2

        # ang_1 is the chosen angle for the new plane
        ang_2 = get_angle_lines(line, next_line)
        ang_3 = get_angle_lines(next_line, next_line.get_next())
        ang_4 = 360 - ang_1 - ang_2 - ang_3

        triangle_1_line_2 = Line(next_line.start, next_line.end)
        triangle_1_line_3 = Line(next_line.end, test_point_b_1)

        triangle_1_ang_3 = get_angle_lines(triangle_1_line_2, triangle_1_line_3)

        t2_ang_1 = ang_3 - triangle_1_ang_3
        t2_ang_2 = ang_4
        t2_ang_3 = 180 - t2_ang_1 - t2_ang_2

        t2_mid = Line(next_line.end, test_point_b_1).get_length()
        t2_side = (t2_mid * math.sin(math.radians(t2_ang_3))) / math.sin(math.radians(t2_ang_2))

        change_line = next_line.get_next()
        angle_c_1 = math.degrees(
            math.asin((change_line.end[1] - change_line.start[1]) / change_line.get_length())
        )

        test_point_c_1 = change_line.start
        opp = math.sin(math.radians(angle_c_1)) * t2_side
        adj = math.sqrt(math.pow(t2_side, 2) - math.pow(opp, 2))

        test_point_c_2 = [test_point_c_1[0] + adj, test_point_c_1[1] + opp]
        if not point_on_line(change_line, test_point_c_2):
            test_point_c_2 = [test_point_c_1[0] - adj, test_point_c_1[1] + opp]
        if not point_on_line(change_line, test_point_c_2):
            test_point_c_2 = [test_point_c_1[0] + adj, test_point_c_1[1] - opp]
        if not point_on_line(change_line, test_point_c_2):
            test_point_c_2 = [test_point_c_1[0] - adj, test_point_c_1[1] - opp]
        if not point_on_line(change_line, test_point_c_2):
            continue

        # Check if the other point is in the plane where you want to put it.
        # If this is not the case we do not draw this and try again
        if not point_on_plane(plane, test_point_c_2):
            # The point is not in the plane so try again!
            continue

        new_plane_1_points = [
            test_point_b_1,
            next_line.start,
            next_line.end,
            test_point_c_2,
        ]
        new_plane_2_points = [
            line.start,
            test_point_b_1,
            test_point_c_2,
            change_line.end,
        ]

        # Check all the lines to see if they are long enough
        # If one or more and too short we don't draw this plane
        length_1 = get_length(new_plane_1_points[0], new_plane_1_points[1])
        length_2 = get_length(new_plane_1_points[1], new_plane_1_points[2])
        length_3 = get_length(new_plane_1_points[2], new_plane_1_points[3])
        length_4 = get_length(new_plane_1_points[3], new_plane_1_points[0])
        length_5 = get_length(new_plane_2_points[0], new_plane_2_points[1])
        length_6 = get_length(new_plane_2_points[1], new_plane_2_points[2])
        length_7 = get_length(new_plane_2_points[2], new_plane_2_points[3])
        length_8 = get_length(new_plane_2_points[3], new_plane_2_points[0])
        if (
            length_1 <= min_line_length
            or length_2 <= min_line_length
            or length_3 <= min_line_length
            or length_4 <= min_line_length
            or length_5 <= min_line_length
            or length_6 <= min_line_length
            or length_7 <= min_line_length
            or length_8 <= min_line_length
        ):
            continue
        plane_1 = Plane(new_plane_1_points, colours[colour_index])
        plane_2 = Plane(new_plane_2_points, plane.get_colour())

        # Check if all the new angles are NOT nice, so not 90.
        # unless you specifically wanted 90 angles
        # Damn floating points :(
        if abs(angle_c_1 - 90) < 0.001 and 90 not in angles:
            continue

        return plane_1, plane_2, plane_choice
    return None, None, None


def background_square_clean(_rand, _width, _height, _index):
    # We will draw a larger square on it's side. The points of the square are:
    # [-width/2, -height/2]
    # [width/2, -height/2]
    # [width/2, height/2]
    # [-width/2, height/2]
    # The square behind this square on it side will have the following points:
    side_triangle = _height / math.sqrt(2)
    point_a = math.pow(side_triangle, 2) - math.pow(_height / 2, 2)
    point_a = math.sqrt(point_a)
    point_a = -(_width / 2) - point_a
    left_point = [point_a, 0]
    point_c = point_a * -1
    right_point = [point_c, 0]
    side_triangle_2 = _width / math.sqrt(2)
    point_b = math.pow(side_triangle_2, 2) - math.pow(_width / 2, 2)
    point_b = math.sqrt(point_b)
    point_b = -(_height / 2) - point_b
    bottom_point = [0, point_b]
    point_d = point_b * -1
    top_point = [0, point_d]

    colour_index = _rand.randint(_index, len(colours) - 1 + _index)
    colour_index -= _index
    _index += 1

    background_points = [left_point, top_point, right_point, bottom_point]
    background_plane = Plane(background_points, colours[colour_index])

    return background_plane


def generate_avatar(file_name, file_path):
    # Code repurposed from https://github.com/Grabot/Stijl
    # The email hash will be the seed of the avatar generation
    random.seed(file_name)
    # Because this will be the default image we will add an indicator that it is the default.
    file_name += "_default"
    planes = []
    # Add an index so that we can pick new colours from the same list
    # using the same seed and get a new one every time.
    index = 0
    # We want the resulting image to be 250x250
    # We initially make it slightly bigger to avoid black corners on the image from outer lines
    width = 252
    height = 252
    background_plane = background_square_clean(random, width, height, index)
    index += 1
    planes.append(background_plane)

    min_squares = 15
    max_squares = 30
    square_numbers = random.randint(min_squares, max_squares)

    for x in range(0, square_numbers):
        plane_1, plane_2, chosen_plane = add_square_clean(random, width, height, planes, index)
        if plane_1 is None and plane_2 is None and chosen_plane is None:
            break
        else:
            del planes[chosen_plane]
            planes.append(plane_1)
            planes.append(plane_2)

    im = Image.new("RGBA", (width * 2, height * 2))
    draw = ImageDraw.Draw(im, "RGBA")
    for plane in planes:
        points = []
        for line in plane.get_all_lines():
            points.append((line.start[0] + width, line.start[1] + height))
        plane_colour = tuple(int(plane.colour.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
        draw.polygon(points, plane_colour, outline="black", width=2)

    del draw

    bound_x = int(width / 2) + 1
    bound_y = int(height / 2) + 1
    # subtract 2 again to make it 250x250
    box = (bound_x, bound_y, bound_x + width - 2, bound_y + height - 2)
    im2 = im.crop(box)

    file = os.path.join(file_path, "%s.png" % file_name)
    im2.save(file)
    os.chmod(file, stat.S_IRWXO)
