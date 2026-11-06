"""New practice material and pure scoring helpers; not original DOS lesson content."""
import random

SPRINT_WORDS = tuple('''apple beach bright button camera candle carpet castle center chair circle clean cloud coffee color corner cotton dance detail dinner doctor dream early earth engine family farmer feather field finish flower forest friend garden gentle golden green guitar hammer happy harbor honest island jacket jungle kitten ladder lantern laptop laugh lemon letter library little magnet market meadow memory middle mirror morning music nature nearby nickel number office orange pencil people picture planet pocket polite purple puzzle quiet rabbit radio random ribbon river rocket school screen secret shadow silver simple sister sketch smooth soccer spring square steady street summer sunset table teacher temple ticket timber travel turtle useful valley velvet violet warm window winter wonder yellow zebra ability balance blanket bridge butter clever collect common curious decide discover distant double eager effort energy equal explore famous focus follow fresh future gather growth handle health history imagine invite journey joyful junior kitchen language listen manage meadow modern motion narrow notice ocean open order paper patient pattern perfect phrase pillow please promise proper reason result rhythm rotate safety season select sentence signal silent skill soften solid solve sparkle spirit stable stage strong sudden support talent target texture thunder tiny tomorrow toward useful venture volume welcome whisper winner wisdom wooden writing'''.split())

SENTENCE_SETS = {
    'Everyday sentences': [
        'The morning sun shines through the kitchen window.',
        'A fresh notebook is ready for another day of practice.',
        'Please place the blue folder beside the desk lamp.',
        'Our neighbors planted flowers along the garden fence.',
        'A steady rhythm helps each finger find its next key.',
    ],
    'School and work': [
        'The teacher wrote a short message on the classroom board.',
        'Every student should review the instructions before beginning.',
        'The meeting starts after everyone has opened their notes.',
        'We saved the final report in the shared project folder.',
        'Careful practice can improve both speed and accuracy.',
    ],
    'Punctuation challenge': [
        'Wait, did you remember the keys, folders, and notes?',
        'The sign said, "Please close the door."',
        'First, check the number; next, read the sentence.',
        'It is 8:30, and the library opens at 9:00.',
        'Great work! Now try another sentence without rushing.',
    ],
    'Longer passages': [
        'During the afternoon, a gentle breeze moved the leaves outside the quiet classroom.',
        'The best typing habits begin with relaxed shoulders, steady hands, and thoughtful practice.',
        'After finishing the first exercise, the student reviewed the report and chose another challenge.',
        'A small improvement every day can lead to greater comfort, confidence, and control at the keyboard.',
        'Before starting the final sentence, take a moment to find the home row and prepare your fingers.',
    ],
}

def make_sprint_round(words=SPRINT_WORDS, previous=(), count=12, rng=None):
    """No duplicates in a round; avoid previous round when pool is large enough."""
    rng = rng or random
    pool = list(dict.fromkeys(words))
    if len(pool) < count:
        raise ValueError('Not enough distinct words for a full round')
    fresh = [word for word in pool if word not in previous]
    if len(fresh) >= count:
        pool = fresh
    return rng.sample(pool, count)

def calculate_score(attempts, seconds):
    """Attempts contain (expected, typed, count_of_wrong_keypresses)."""
    expected = sum(len(item[0]) for item in attempts)
    actual = sum(len(item[1]) for item in attempts)
    errors = sum(sum(a != b for a,b in zip(item[0],item[1])) + abs(len(item[0])-len(item[1])) for item in attempts)
    return {'wpm': round((actual / 5) * 60 / max(seconds,0.01),1),
            'accuracy': round(100 * max(0, expected-errors) / expected,1) if expected else 0.,
            'errors': errors,'key_mistakes':sum(item[2] for item in attempts)}
