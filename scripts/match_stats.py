from requests_html import HTMLSession
import pandas as pd
import logging

s = HTMLSession()

def get_match_links(url):
    ''' Returns [['men' or 'women' , 'link']]'''
    r = s.get(url)
    match_links = []
    matches = r.html.find('a.vbw-mu__status-info-btn')
    logging.info('Getting Match Links')
    print('Getting Match Links')
    for match in matches:
        link = 'https://en.volleyballworld.com' + match.attrs['data-matchurl']
        division = match.find('div.vbw-mu__info--details', first=True).text.split(' - ')[-1]
        match_links.append([division, link])
    return match_links

def get_match_team_stats(url):    
    r = s.get(url)
    r.html.render(sleep=5)

    try:
        division = r.html.find('div.vbw-mu__info--details', first=True).text.split(' - ')[-1]

        team_a = r.html.find('div.vbw-mu__team--home div.vbw-mu__team__name', first=True).text
        score_a = r.html.find('div.vbw-mu__score--home', first=True).text
        
        team_b = r.html.find('div.vbw-mu__team--away div.vbw-mu__team__name', first=True).text
        score_b = r.html.find('div.vbw-mu__score--away', first=True).text

        logging.info(f'Getting Data From Match: {team_a} - {team_b} ({division})')
        print(f'Getting Data From Match: {team_a} vs {team_b} ({division})')

        set_scores = r.html.find('div.vbw-mu__sets div')
        set_scores_a, set_scores_b = [], []
        for score in set_scores:
            if score.text == '-': 
                break
            else:
                scores = score.text.split('-')
                set_scores_a.append(int(scores[0]))
                set_scores_b.append(int(scores[1]))

        team_a_stats, team_b_stats = [], []
        stat_list = ['attack', 'block', 'serve', 'opponent-error', 'total', 'dig', 'reception', 'set']

        for st in stat_list:
            stats = r.html.find(f'tr.{st} td.stats-score')
            team_a_stats.append(stats[0].text)
            team_b_stats.append(stats[1].text)

        # team, opponent, division, sets_won, [sets_scores], attacks, blocks, aces, opp_errors, total_points, digs, receptions, sets, errors_committed, opp_points
        data_one = [team_a, team_b, division, score_a, set_scores_a, team_a_stats[0], team_a_stats[1], team_a_stats[2], 
                    team_a_stats[3], team_a_stats[4], team_a_stats[5], team_a_stats[6], team_a_stats[7], team_b_stats[3], team_b_stats[4]]
        data_two = [team_b, team_a, division, score_b, set_scores_b, team_b_stats[0], team_b_stats[1], team_b_stats[2], 
                    team_b_stats[3], team_b_stats[4], team_b_stats[5], team_b_stats[6], team_b_stats[7], team_a_stats[3], team_a_stats[4]]

        return data_one, data_two
    
    except:
        stage = r.html.find('div.vbw-mu__info--details', first=True).text.split(' - ')[0]
        division = r.html.find('div.vbw-mu__info--details', first=True).text.split(' - ')[-1]
        team_a = r.html.find('div.vbw-mu__team--home div.vbw-mu__team__name', first=True).text
        team_b = r.html.find('div.vbw-mu__team--away div.vbw-mu__team__name', first=True).text
        logging.warning(f'Error: {stage} - {team_a} vs {team_b} ({division}) {url}')
        print(f'Error: {stage} - {team_a} vs {team_b} ({division})')   

        return None, None

def main():
    
    logging.basicConfig(filename='match_stats_log.log', encoding='utf-8', level=logging.INFO)
    
    
    url = 'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/schedule/'
    
    # trial_links = [['Women', 'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/schedule/13851/'],
    #                ['Men', 'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/schedule/13714/'],
    #                ['Women', 'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/schedule/13841/'],
    #                ['Women', 'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/schedule/13838/'],
    #                ['Men', 'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/schedule/13698/'],
    #                ['Women', 'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/schedule/13815/']]

    # try: unfinished match
    
    
    match_links = get_match_links(url)
    match_data = []
    for division, link in match_links: ##
        if division == 'Men': ## EDIT THIS WHEN SCRAPING MEN'S DIVISION LATER
            data_one, data_two = get_match_team_stats(link) 
            if data_one != None: match_data.append(data_one) ## get_match_team_stats returns None if Error
            if data_two != None: match_data.append(data_two)
    col_names = ['team', 'opponent', 'division', 'sets_won', 'sets_scores', 'attacks', 'blocks', 'aces', 'opp_errors', 'total_points', 'digs', 'receptions', 'sets', 'err_committed', 'opp_points']
    df = pd.DataFrame(match_data, columns=col_names)
    df.to_csv('match_data_m.csv', index=False)
    
    
if __name__ == '__main__':
   main()