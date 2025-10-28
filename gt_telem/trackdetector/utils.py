# Portions of this file are adapted from gt7telemetry by Bornhall:
#   https://github.com/Bornhall/gt7telemetry/blob/main/gt7trackdetect.py

MAX_MATCHES = 3
ALLOWED_IOU_DEVIATION = 0.02

class TrackBounds:
	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			# Convert the value to the appropriate data type
			if key in ['TRACK']:
				value = int(value)
			elif key in ['DIRECTION']:
				value = str(value)
			else:
				value = float(value)

			# Set the attribute on the instance
			setattr(self, key, value)

def find_matching_track(L1X, L1Y, L2X, L2Y, MinX, MinY, MaxX, MaxY, track_bounds):
	outer_bounding_box = get_bounding_box(MinX, MinY, MaxX, MaxY)

	matches = []
	for element in track_bounds:
		inner_bounding_box = get_bounding_box(element.MINX, element.MINY, element.MAXX, element.MAXY)
		intersects, direction = line_intersects(element.P1X, element.P1Y, element.P2X, element.P2Y, L1X, L1Y, L2X, L2Y)
		if intersects == 0 or element.DIRECTION != direction:
			continue

		iou = calculate_iou(outer_bounding_box, inner_bounding_box)
		matches.append((iou, element.TRACK))

	if not matches:
		return []

	matches.sort(key=lambda x: x[0], reverse=True)
	best_match_iou = matches[0][0]
	iou_threshold = best_match_iou * (1 - ALLOWED_IOU_DEVIATION)

	# Filter out matches that are not within 2-3% of the best match
	filtered_matches = [match for match in matches if match[0] >= iou_threshold]
	return filtered_matches[:MAX_MATCHES]

def calculate_iou(outer_bounding_box, inner_bounding_box):
	intersection = get_bounding_box_intersection(outer_bounding_box, inner_bounding_box)
	intersection_area = get_bounding_box_area(intersection)
	union_area = get_bounding_box_area(outer_bounding_box) + get_bounding_box_area(inner_bounding_box) - intersection_area
	return intersection_area / union_area

def line_intersects(p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
	s1_x = p1_x - p0_x
	s1_y = p1_y - p0_y
	s2_x = p3_x - p2_x
	s2_y = p3_y - p2_y

	denominator = -s2_x * s1_y + s1_x * s2_y
	if denominator == 0:
		# Lines are parallel or coincident, no intersection
		return (0, '--')

	s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / denominator
	t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / denominator
	d = get_direction(s2_x, s2_y)

	if s >= 0 and s <= 1 and t >= 0 and t <= 1:
		# Collision detected
		return (1, d)
	return (0, d) # No collision

def get_bounding_box(x1, y1, x2, y2):
	return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

def get_bounding_box_area(box):
	return (box[2] - box[0]) * (box[3] - box[1])

def get_bounding_box_intersection(box1, box2):
	left = max(box1[0], box2[0])
	right = min(box1[2], box2[2])
	top = max(box1[1], box2[1])
	bottom = min(box1[3], box2[3])
	if left > right or top > bottom:
		# The bounding boxes do not overlap
		return 0, 0, 0, 0
	return left, top, right, bottom

def get_direction(s2_x: float, s2_y: float) -> str:
    if s2_x > 0:
        return 'PX'
    elif s2_x < 0:
        return 'NX'
    elif s2_y > 0:
        return 'PY'
    elif s2_y < 0:
        return 'NY'
    return '--'
