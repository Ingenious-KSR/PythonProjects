def count_player_a_wins(N, S):
    # Define the win rules
    win_rules = {
        ('snake', 'water'): 'A',
        ('water', 'snake'): 'B',
        ('water', 'gun'): 'A',
        ('gun', 'water'): 'B',
        ('gun', 'snake'): 'A',
        ('snake', 'gun'): 'B'
    }
    
    # Count wins for Player A
    a_wins = 0
    
    # Iterate through each round
    n = len(S)
    i=0
    while i<n:
        str1 = S[i:i + 5] if (i+5) < n else ''
        print(str1) 
        str2 = S[i:i+3] if (i+3) < n else ''
        print(str2)
        if str1 == 'water' or str1 == 'snake':
            move_a = str1
            i += 5
            str3 = S[i:i + 5] if (i+5) < n else ''
            str4 = S[i:i+3] if (i+3) < n else ''
            if str3 == 'water' or str3 == 'snake':
                move_b = str3
                i += 5
            else:
                move_b = str4
                i += 3
        else:
            move_a = str2
            i += 3
            str3 = S[i:i + 5] if (i+5) < n else ''
            str4 = S[i:i+3] if (i+3) < n else ''
            if str3 == 'water' or str3 == 'snake':
                move_b = str3
                i += 5
            else:
                move_b = str4
                i += 3
        if (move_a, move_b) in win_rules:
            if win_rules[(move_a, move_b)] == 'A':
                a_wins +=1
                
    return a_wins

# Example usage
input1 = 3
input2 = "watergunwaterwatergunwater"

print(count_player_a_wins(input1, input2))