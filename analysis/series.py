from .gt_solver import solve

# Calculates chances of winning bo3 match after ban
def conquest_bo3 (mups, h1, h2, v1, v2):
    return (mups[h1][v1] * mups[h2][v1] * (2 - mups[h1][v2] - mups[h2][v2]) + \
            mups[h1][v2] * mups[h2][v2] * (2 - mups[h1][v1] - mups[h2][v1]) + \
            mups[h1][v1] * mups[h2][v2] + mups[h1][v2] * mups[h2][v1]) * 0.5

# Calculates chances of winning bo5 match after ban
def conquest_bo5 (mups, h1, h2, h3, v1, v2, v3):
    
    ### game 1

    A = (mups[h1][v1] + mups[h1][v2] + mups[h1][v3])/9
    B = (mups[h2][v1] + mups[h2][v2] + mups[h2][v3])/9
    C = (mups[h3][v1] + mups[h3][v2] + mups[h3][v3])/9

    D = (3 - mups[h1][v1] - mups[h2][v1] - mups[h3][v1])/9
    E = (3 - mups[h1][v2] - mups[h2][v2] - mups[h3][v2])/9
    F = (3 - mups[h1][v3] - mups[h2][v3] - mups[h3][v3])/9

    ### game 2

    AB = (A*(mups[h2][v1] + mups[h2][v2] + mups[h2][v3]) + \
          B*(mups[h1][v1] + mups[h1][v2] + mups[h1][v3]))/6
    AC = (A*(mups[h3][v1] + mups[h3][v2] + mups[h3][v3]) + \
          C*(mups[h1][v1] + mups[h1][v2] + mups[h1][v3]))/6
    BC = (B*(mups[h3][v1] + mups[h3][v2] + mups[h3][v3]) + \
          C*(mups[h2][v1] + mups[h2][v2] + mups[h2][v3]))/6

    AD = (A*(2 - mups[h2][v1] - mups[h3][v1]) + \
          D*(mups[h1][v2] + mups[h1][v3]))/6
    AE = (A*(2 - mups[h2][v2] - mups[h3][v2]) + \
          E*(mups[h1][v1] + mups[h1][v3]))/6
    AF = (A*(2 - mups[h2][v3] - mups[h3][v3]) + \
          F*(mups[h1][v1] + mups[h1][v2]))/6
    BD = (B*(2 - mups[h1][v1] - mups[h3][v1]) + \
          D*(mups[h2][v2] + mups[h2][v3]))/6
    BE = (B*(2 - mups[h1][v2] - mups[h3][v2]) + \
          E*(mups[h2][v1] + mups[h2][v3]))/6
    BF = (B*(2 - mups[h1][v3] - mups[h3][v3]) + \
          F*(mups[h2][v1] + mups[h2][v2]))/6
    CD = (C*(2 - mups[h1][v1] - mups[h2][v1]) + \
          D*(mups[h3][v2] + mups[h3][v3]))/6
    CE = (C*(2 - mups[h1][v2] - mups[h2][v2]) + \
          E*(mups[h3][v1] + mups[h3][v3]))/6
    CF = (C*(2 - mups[h1][v3] - mups[h2][v3]) + \
          F*(mups[h3][v1] + mups[h3][v2]))/6

    DE = (D*(3 - mups[h1][v2] - mups[h2][v2] - mups[h3][v2]) + \
          E*(3 - mups[h1][v1] - mups[h2][v1] - mups[h3][v1]))/6
    DF = (D*(3 - mups[h1][v3] - mups[h2][v3] - mups[h3][v3]) + \
          F*(3 - mups[h1][v1] - mups[h2][v1] - mups[h3][v1]))/6
    EF = (E*(3 - mups[h1][v3] - mups[h2][v3] - mups[h3][v3]) + \
          F*(3 - mups[h1][v2] - mups[h2][v2] - mups[h3][v2]))/6

    ### game 3

    ABC = (AB*(mups[h3][v1] + mups[h3][v2] + mups[h3][v3]) + \
           AC*(mups[h2][v1] + mups[h2][v2] + mups[h2][v3]) + \
           BC*(mups[h1][v1] + mups[h1][v2] + mups[h1][v3]))/3

    ABD = AB*(1 - mups[h3][v1])/3 + AD*(mups[h2][v2] + mups[h2][v3])/4 + \
                                    BD*(mups[h1][v2] + mups[h1][v3])/4
    ABE = AB*(1 - mups[h3][v2])/3 + AE*(mups[h2][v1] + mups[h2][v3])/4 + \
                                    BE*(mups[h1][v1] + mups[h1][v3])/4
    ABF = AB*(1 - mups[h3][v3])/3 + AF*(mups[h2][v1] + mups[h2][v2])/4 + \
                                    BF*(mups[h1][v1] + mups[h1][v2])/4
    ACD = AC*(1 - mups[h2][v1])/3 + AD*(mups[h3][v2] + mups[h3][v3])/4 + \
                                    CD*(mups[h1][v2] + mups[h1][v3])/4
    ACE = AC*(1 - mups[h2][v2])/3 + AE*(mups[h3][v1] + mups[h3][v3])/4 + \
                                    CE*(mups[h1][v1] + mups[h1][v3])/4
    ACF = AC*(1 - mups[h2][v3])/3 + AF*(mups[h3][v1] + mups[h3][v2])/4 + \
                                    CF*(mups[h1][v1] + mups[h1][v2])/4
    BCD = BC*(1 - mups[h1][v1])/3 + BD*(mups[h3][v2] + mups[h3][v3])/4 + \
                                    CD*(mups[h2][v2] + mups[h2][v3])/4
    BCE = BC*(1 - mups[h1][v2])/3 + BE*(mups[h3][v1] + mups[h3][v3])/4 + \
                                    CE*(mups[h2][v1] + mups[h2][v3])/4
    BCF = BC*(1 - mups[h1][v3])/3 + BF*(mups[h3][v1] + mups[h3][v2])/4 + \
                                    CF*(mups[h2][v1] + mups[h2][v2])/4

    ADE = AD*(2 - mups[h2][v2] - mups[h3][v2])/4 + \
          AE*(2 - mups[h2][v1] - mups[h3][v1])/4 + DE*(mups[h1][v3])/3
    ADF = AD*(2 - mups[h2][v3] - mups[h3][v3])/4 + \
          AF*(2 - mups[h2][v1] - mups[h3][v1])/4 + DF*(mups[h1][v2])/3
    AEF = AE*(2 - mups[h2][v3] - mups[h3][v3])/4 + \
          AF*(2 - mups[h2][v2] - mups[h3][v2])/4 + EF*(mups[h1][v1])/3
    BDE = BD*(2 - mups[h1][v2] - mups[h3][v2])/4 + \
          BE*(2 - mups[h1][v1] - mups[h3][v1])/4 + DE*(mups[h2][v3])/3
    BDF = BD*(2 - mups[h1][v3] - mups[h3][v3])/4 + \
          BF*(2 - mups[h1][v1] - mups[h3][v1])/4 + DF*(mups[h2][v2])/3
    BEF = BE*(2 - mups[h1][v3] - mups[h3][v3])/4 + \
          BF*(2 - mups[h1][v2] - mups[h3][v2])/4 + EF*(mups[h2][v1])/3
    CDE = CD*(2 - mups[h1][v2] - mups[h2][v2])/4 + \
          CE*(2 - mups[h1][v1] - mups[h2][v1])/4 + DE*(mups[h3][v3])/3
    CDF = CD*(2 - mups[h1][v3] - mups[h2][v3])/4 + \
          CF*(2 - mups[h1][v1] - mups[h2][v1])/4 + DF*(mups[h3][v2])/3
    CEF = CE*(2 - mups[h1][v3] - mups[h2][v3])/4 + \
          CF*(2 - mups[h1][v2] - mups[h2][v2])/4 + EF*(mups[h3][v1])/3
    '''
    DEF = (DE*(3 - mups[h1][v3] - mups[h2][v3] - mups[h3][v3]) + \
           DF*(3 - mups[h1][v2] - mups[h2][v2] - mups[h3][v2]) + \
           EF*(3 - mups[h1][v1] - mups[h2][v1] - mups[h3][v1]))/3
    '''
    ### game 4

    ABCD = (ABD*(mups[h3][v2] + mups[h3][v3]) + \
            ACD*(mups[h2][v2] + mups[h2][v3]) + \
            BCD*(mups[h1][v2] + mups[h1][v3]))/2
    ABCE = (ABE*(mups[h3][v1] + mups[h3][v3]) + \
            ACE*(mups[h2][v1] + mups[h2][v3]) + \
            BCE*(mups[h1][v1] + mups[h1][v3]))/2
    ABCF = (ABF*(mups[h3][v1] + mups[h3][v2]) + \
            ACF*(mups[h2][v1] + mups[h2][v2]) + \
            BCF*(mups[h1][v1] + mups[h1][v2]))/2

    ABDE = (ABD*(1 - mups[h3][v2]) + ABE*(1 - mups[h3][v1]) + \
            ADE*mups[h2][v3] + BDE*mups[h1][v3])/2
    ABDF = (ABD*(1 - mups[h3][v3]) + ABF*(1 - mups[h3][v1]) + \
            ADF*mups[h2][v2] + BDF*mups[h1][v2])/2
    ABEF = (ABE*(1 - mups[h3][v3]) + ABF*(1 - mups[h3][v2]) + \
            AEF*mups[h2][v1] + BEF*mups[h1][v1])/2
    ACDE = (ACD*(1 - mups[h2][v2]) + ACE*(1 - mups[h2][v1]) + \
            ADE*mups[h3][v3] + CDE*mups[h1][v3])/2
    ACDF = (ACD*(1 - mups[h2][v3]) + ACF*(1 - mups[h2][v1]) + \
            ADF*mups[h3][v2] + CDF*mups[h1][v2])/2
    ACEF = (ACE*(1 - mups[h2][v3]) + ACF*(1 - mups[h2][v2]) + \
            AEF*mups[h3][v1] + CEF*mups[h1][v1])/2
    BCDE = (BCD*(1 - mups[h1][v2]) + BCE*(1 - mups[h1][v1]) + \
            BDE*mups[h3][v3] + CDE*mups[h2][v3])/2
    BCDF = (BCD*(1 - mups[h1][v3]) + BCF*(1 - mups[h1][v1]) + \
            BDF*mups[h3][v2] + CDF*mups[h2][v2])/2
    BCEF = (BCE*(1 - mups[h1][v3]) + BCF*(1 - mups[h1][v2]) + \
            BEF*mups[h3][v1] + CEF*mups[h2][v1])/2
    '''
    ADEF = (ADE*(2 - mups[h2][v3] - mups[h3][v3]) + \
            ADF*(2 - mups[h2][v2] - mups[h3][v2]) + \
            AEF*(2 - mups[h2][v1] - mups[h3][v1]))/2
    BDEF = (BDE*(2 - mups[h1][v3] - mups[h3][v3]) + \
            BDF*(2 - mups[h1][v2] - mups[h3][v2]) + \
            BEF*(2 - mups[h1][v1] - mups[h3][v1]))/2
    CDEF = (CDE*(2 - mups[h1][v3] - mups[h2][v3]) + \
            CDF*(2 - mups[h1][v2] - mups[h2][v2]) + \
            CEF*(2 - mups[h1][v1] - mups[h2][v1]))/2
    '''
    ### game 5

    ABCDE = ABDE*mups[h3][v3] + ACDE*mups[h2][v3] + BCDE*mups[h1][v3]
    ABCDF = ABDF*mups[h3][v2] + ACDF*mups[h2][v2] + BCDF*mups[h1][v2]
    ABCEF = ABEF*mups[h3][v1] + ACEF*mups[h2][v1] + BCEF*mups[h1][v1]
    '''
    ABDEF = ABDE*(1 - mups[h3][v3]) + ABDF*(1 - mups[h3][v2]) + \
            ABEF*(1 - mups[h3][v1])
    ACDEF = ACDE*(1 - mups[h2][v3]) + ACDF*(1 - mups[h2][v2]) + \
            ACEF*(1 - mups[h2][v1])
    BCDEF = BCDE*(1 - mups[h1][v3]) + BCDF*(1 - mups[h1][v2]) + \
            BCEF*(1 - mups[h1][v1])
    '''
    return ABC + ABCD + ABCE + ABCF + ABCDE + ABCDF + ABCEF

# Fixes Player 1 deck whilst Player 2 remains random
# Should be about the same result as both random-ing but has a small error margin
def conquest_bo5_fixed(mups, h1, h2, h3, v1, v2, v3):

    ### game 1

    A = (mups[h1][v1] + mups[h1][v2] + mups[h1][v3])/3

    D = (1 - mups[h1][v1])/3
    E = (1 - mups[h1][v2])/3
    F = (1 - mups[h1][v3])/3

    ### game 2

    AB = (A*(mups[h2][v1] + mups[h2][v2] + mups[h2][v3]))/3

    AD = (A*(1 - mups[h2][v1])/3) + \
         (D*(mups[h1][v2] + mups[h1][v3])/2)
    AE = (A*(1 - mups[h2][v2])/3) + \
         (E*(mups[h1][v1] + mups[h1][v3])/2)
    AF = (A*(1 - mups[h2][v3])/3) + \
         (F*(mups[h1][v1] + mups[h1][v2])/2)

    DE = (D*(1 - mups[h1][v2]) + \
          E*(1 - mups[h1][v1]))/2
    DF = (D*(1 - mups[h1][v3]) + \
          F*(1 - mups[h1][v1]))/2
    EF = (E*(1 - mups[h1][v3]) + \
          F*(1 - mups[h1][v2]))/2

    ### game 3

    ABC = (AB*(mups[h3][v1] + mups[h3][v2] + mups[h3][v3]))/3

    ABD = AB*(1 - mups[h3][v1])/3 + AD*(mups[h2][v2] + mups[h2][v3])/2
    ABE = AB*(1 - mups[h3][v2])/3 + AE*(mups[h2][v1] + mups[h2][v3])/2
    ABF = AB*(1 - mups[h3][v3])/3 + AF*(mups[h2][v1] + mups[h2][v2])/2

    ADE = AD*(1 - mups[h2][v2])/2 + \
          AE*(1 - mups[h2][v1])/2 + DE*(mups[h1][v3])
    ADF = AD*(1 - mups[h2][v3])/2 + \
          AF*(1 - mups[h2][v1])/2 + DF*(mups[h1][v2])
    AEF = AE*(1 - mups[h2][v3])/2 + \
          AF*(1 - mups[h2][v2])/2 + EF*(mups[h1][v1])
    '''
    DEF = (DE*(1 - mups[h1][v3]) + \
           DF*(1 - mups[h1][v2]) + \
           EF*(1 - mups[h1][v1]))
    '''
    ### game 4

    ABCD = (ABD*(mups[h3][v2] + mups[h3][v3]))/2
    ABCE = (ABE*(mups[h3][v1] + mups[h3][v3]))/2
    ABCF = (ABF*(mups[h3][v1] + mups[h3][v2]))/2

    ABDE = (ABD*(1 - mups[h3][v2]) + ABE*(1 - mups[h3][v1]))/2 + \
            ADE*mups[h2][v3]
    ABDF = (ABD*(1 - mups[h3][v3]) + ABF*(1 - mups[h3][v1]))/2 + \
            ADF*mups[h2][v2]
    ABEF = (ABE*(1 - mups[h3][v3]) + ABF*(1 - mups[h3][v2]))/2 + \
            AEF*mups[h2][v1]
    '''
    ADEF = (ADE*(1 - mups[h2][v3]) + \
            ADF*(1 - mups[h2][v2]) + \
            AEF*(1 - mups[h2][v1]))
    '''
    ### game 5

    ABCDE = ABDE*mups[h3][v3]
    ABCDF = ABDF*mups[h3][v2]
    ABCEF = ABEF*mups[h3][v1]
    '''
    ABDEF = ABDE*(1 - mups[h3][v3]) + ABDF*(1 - mups[h3][v2]) + \
            ABEF*(1 - mups[h3][v1])
    '''
    return ABC + ABCD + ABCE + ABCF + ABCDE + ABCDF + ABCEF

# Calculates chances of winning for each ban option on the most standard format
def banList_bo5(mups, hero_decks, villain_decks):
    final = [[] for _ in range(4)]

    for i in range(4):
        h_subset = hero_decks[:i] + hero_decks[i+1:]
        for j in range(4):
            v_subset = villain_decks[:j] + villain_decks[j+1:]
            final[i].append(conquest_bo5(mups, *h_subset, *v_subset))

    return final

# Calculates chances of winning for each ban option on the most standard format
# Utilizes fixed results function
def banList_bo5_fixed (mups, hero_decks, villain_decks):
    final = [[] for _ in range(4)]

    for i in range(4):
        h_subset = hero_decks[:i] + hero_decks[i+1:]
        for j in range(4):
            v_subset = villain_decks[:j] + villain_decks[j+1:]
            final[i].append(conquest_bo5_fixed(mups, *h_subset, *v_subset))

    return final

# Calculates chances of winning for each ban option on bo3 format
def banList_bo3 (mups, hero_decks, villain_decks):
    final = [[] for _ in range(3)]

    for i in range(3):
        h_subset = hero_decks[:i] + hero_decks[i+1:]
        for j in range(3):
            v_subset = villain_decks[:j] + villain_decks[j+1:]
            final[i].append(conquest_bo3(mups, *h_subset, *v_subset))

    return final

# Recursive function to solve Last Hero Standing format
def lhs_rec (mups, h_decks, h_size, v_decks, v_size, active):
      current_match = mups[h_decks[active[0]]][v_decks[active[1]]]
      # If you win
      new_v_size = v_size - 1


      # win = chances of winning set if wins current game
      if (new_v_size == 0):
            win = current_match
      else:
            new_v_decks = v_decks.copy()
            new_v_decks.remove(v_decks[active[1]])
            new_active = active.copy()
            win_rest = 1
            for deck in range(len(new_v_decks)):
                  new_active[1] = deck
                  temp = lhs_rec(mups, h_decks, h_size, new_v_decks, new_v_size, new_active)
                  if (temp < win_rest):
                        win_rest = temp

            lhs_rec.count += 1
            win = current_match * win_rest


      # If you lose
      new_h_size = h_size - 1

      # lose = chances of winning set if losing current game
      if (new_h_size == 0):
            lose = 0
      else:
            new_h_decks = h_decks.copy()
            new_h_decks.remove(h_decks[active[0]])
            new_active = active.copy()
            win_rest = 0
            for deck in range(len(new_h_decks)):
                  new_active[0] = deck
                  temp = lhs_rec(mups, new_h_decks, new_h_size, v_decks, v_size, new_active)
                  if (temp > win_rest):
                        win_rest = temp

            lhs_rec.count += 1
            lose = (1 - current_match) * win_rest
      
      
      return win + lose

# Last Hero Standing first pick
def lhs_first_pick(mups, h_decks, h_size, v_decks, v_size):
      lhs_rec.count = 0
      fp = []
      for i in range(h_size):
            fp.append([])
            for j in range (v_size):
                  active = [i, j]
                  fp[i].append(lhs_rec(mups, h_decks, h_size, v_decks, v_size, active))
      return fp

# Last Hero Standing format
def lhs_ban_list(mups, h_decks, h_size, v_decks, v_size):
      bl = []
      new_h_size = h_size - 1
      new_v_size = v_size - 1
      for i in range(v_size):
            bl.append([])
            new_v_decks = v_decks.copy()
            new_v_decks.remove(v_decks[i])
            for j in range (h_size):
                  new_h_decks = h_decks.copy()
                  new_h_decks.remove(h_decks[j])
                  bl[i].append(solve(lhs_first_pick(mups, new_h_decks, new_h_size, new_v_decks, new_v_size))[2])
      return bl

# Generic conquest, not as efficient
def conquest_recursive(mups, h_decks, v_decks):
      if (h_decks == []):
            return 1
      if (v_decks == []):
            return 0
      
      total = len(h_decks) * len(v_decks)
      winning_chance = 0

      # Chances of winning with each hero deck
      for h_deck in h_decks:
            deck_win = 0
            for v_deck in v_decks:
                  deck_win += mups[h_deck][v_deck]
            deck_win = deck_win / total
            new_h_decks = h_decks.copy()
            new_h_decks.remove(h_deck)
            winning_chance += deck_win * conquest_recursive(mups, new_h_decks, v_decks)

      # Chance of winning with each villain deck
      for v_deck in v_decks:
            deck_win = 0
            for h_deck in h_decks:
                  deck_win += mups[v_deck][h_deck]
            deck_win = deck_win / total
            new_v_decks = v_decks.copy()
            new_v_decks.remove(v_deck)
            winning_chance += deck_win * conquest_recursive(mups, h_decks, new_v_decks)
      
      return winning_chance

# Calculates chances of winning for each ban option on bo7 format
def banList_bo7 (mups, hero_decks, villain_decks):
    final = [[] for _ in range(5)]

    for i in range(5):
        h_subset = hero_decks[:i] + hero_decks[i+1:]
        for j in range(5):
            v_subset = villain_decks[:j] + villain_decks[j+1:]
            final[i].append(conquest_recursive(mups, *h_subset, *v_subset))

    return final
