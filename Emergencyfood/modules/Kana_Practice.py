import random

#sounds
baseSounds = {'hiragana':'あ い う え お'.split(), 'katakana':'ア イ ウ エ オ'.split(), 'answers':'a i u e o'.split()}
kSounds = {'hiragana':'か き く け こ'.split(), 'katakana':'カ キ ク ケ コ'.split(), 'answers':'ka ki ku ke ko'.split()}
sSounds = {'hiragana':'さ し す せ そ'.split(), 'katakana':'サ シ ス セ ソ'.split(), 'answers':'sa shi su se so'.split()}
tSounds = {'hiragana':'た ち つ て と'.split(), 'katakana':'タ チ ツ テ ト'.split(), 'answers':'ta chi tsu te to'.split()}
nSounds = {'hiragana':'な に ぬ ね の'.split(), 'katakana':'ナ ニ ヌ ネ ノ'.split(), 'answers':'na ni nu ne no'.split()}
hSounds = {'hiragana':'は ひ ふ へ ほ'.split(), 'katakana':'ハ ヒ フ ヘ ホ'.split(), 'answers':'ha hi fu he ho'.split()}
mSounds = {'hiragana':'ま み む め も'.split(), 'katakana':'マ ミ ム メ モ'.split(), 'answers':'ma mi mu me mo'.split()}
ySounds = {'hiragana':'や ゆ よ'.split(), 'katakana':'ヤ ユ ヨ'.split(), 'answers':'ya yu yo'.split()}
rSounds = {'hiragana':'ら り る れ ろ'.split(), 'katakana':'ラ リ ル レ ロ'.split(), 'answers':'ra ri ru re ro'.split()}
wSounds = {'hiragana':'わ を'.split(), 'katakana':'ワ ヲ'.split(), 'answers':'wa wo'.split()}
nSound = {'hiragana':'ん', 'katakana':'ン', 'answers':'n'}

#kana list
kana = [baseSounds, kSounds, sSounds, tSounds, nSounds, hSounds, mSounds, ySounds, rSounds, wSounds, nSound]

#prints the question
async def getQuestion(mode):
    soundCategory = random.randint(0, len(kana)-1)
    questionCat = kana[soundCategory][mode]
    shuffledQuestionCat = random.sample(questionCat, len(questionCat))
    toRemove = random.randint(0, len(questionCat)-1)
    answer = kana[soundCategory]['answers'][toRemove]
    questionContent = ' '.join(shuffledQuestionCat)
    
    if kana[soundCategory] == nSound:
        question = '\nWhat is the sound of this kana?(ex: for あ type "a")'
        questionContent = questionCat[toRemove]+question
    
    else:
        question = '\nWhat is the sound of the missing kana?(ex: for あ type "a")'
        questionContent = questionContent.replace(questionCat[toRemove], ' _ ')+question
    
    return questionContent, answer