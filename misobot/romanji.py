import pykakasi

async def romanji(text):
    kks = pykakasi.kakasi()
    res = []
    result = kks.convert(text)
    for item in result:
        res.append(item['hepburn'])
    sentence = ' '.join(res)
    return sentence

if __name__ == "__main__":
    print(romanji('かな漢字'))