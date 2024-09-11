import os

def load_unicode_to_cns():
    unicode_to_cns = {}
    unicode_files = ['CNS2UNICODE_Unicode BMP.txt', 'CNS2UNICODE_Unicode 2.txt', 'CNS2UNICODE_Unicode 15.txt']
    
    for file in unicode_files:
        file_path = os.path.join('datatool', file)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                cns, unicode = line.strip().split('\t')
                unicode = unicode.upper()
                if unicode.startswith('U+'):
                    unicode = unicode[2:]
                unicode_to_cns[unicode] = cns
    
    return unicode_to_cns

def load_cns_to_bopomofo():
    cns_to_bopomofo = {}
    
    file_path = os.path.join('datatool', 'CNS_phonetic.txt')
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            cns, phonetic = line.strip().split('\t')
            if cns in cns_to_bopomofo:
                cns_to_bopomofo[cns].append(phonetic)
            else:
                cns_to_bopomofo[cns] = [phonetic]
    
    return cns_to_bopomofo

def create_unicode_to_bopomofo():
    unicode_to_cns = load_unicode_to_cns()
    cns_to_bopomofo = load_cns_to_bopomofo()
    
    output_dir = os.path.join('ShowBopomofo.glyphsReporter', 'Contents', 'Resources')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'unicode_to_bopomofo.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for unicode, cns in unicode_to_cns.items():
            if cns in cns_to_bopomofo:
                bopomofo_list = cns_to_bopomofo[cns]
                bopomofo_str = ','.join(bopomofo_list)
                f.write(f"{unicode}\t{bopomofo_str}\n")

if __name__ == "__main__":
    create_unicode_to_bopomofo()
    print("轉換完成。結果已保存到 ShowBopomofo.glyphsReporter/Contents/Resources/unicode_to_bopomofo.txt 文件中。")