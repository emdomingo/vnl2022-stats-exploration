from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging
import time

###
# NOTE: Trouble with Turkiye and Turkey
###

def get_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    return soup

def get_team_links(url):
    soup = get_soup(url)
    team_links = []
    teams = soup.select('div.vbw-team-list a')
    for team in teams:
        link = 'https://en.volleyballworld.com' + team['href']
        country = team.find('div', class_='vbw-mu__team__name').text
        team_links.append([link, country])
    return team_links

def get_player_links(url):  
    soup = get_soup(url)
    player_links = []
    players = soup.select('td.playername a')
    for player in players:
        link = 'https://en.volleyballworld.com' +  player['href']
        name = player.text
        player_links.append([link, name])
    return player_links

def get_player_bio_stats(url):
    soup = get_soup(url)
    try:
        # GETTING PLAYER BIO
        player_number = soup.find('div', class_='vbw-player-no').text
        first_name = soup.find('h3', class_='vbw-player-name').text
        last_name = soup.find('h3', class_='vbw-player-lastname').text

        player_bio = soup.select('div.vbw-player-bio-text')

        position = player_bio[0].text
        nationality = player_bio[2].text
        if nationality == 'Turkey': nationality = 'Türkiye'
        age = player_bio[4].text
        birthdate = player_bio[5].text
        height_cm = player_bio[6].text.replace('cm', '')
        weight_kg = player_bio[7].text.replace('Kg', '')

        bio_dict = {
            'player_number' : player_number,
            'first_name' : first_name,
            'last_name' : last_name,
            'position' : position,
            'nationality' : nationality,
            'age' : age,
            'birthdate' : birthdate,
            'height_cm' : height_cm,
            'weight_kg' : weight_kg
        }

        ## MATCH DATA

        # OPPONENT DATA
        teama, teamb, opponents = [], [], []
        teama_list = soup.select('div[data-tab="scoring"] td.teama')
        for team in teama_list:
            teama.append(team.find('div', class_='vbw-mu__team__name').text)
        teamb_list = soup.select('div[data-tab="scoring"] td.teamb')
        for team in teamb_list:
            teamb.append(team.find('div', class_='vbw-mu__team__name').text)
        for i in range(0, len(teama)):
            opponents.append(teama[i]) if nationality != teama[i] else opponents.append(teamb[i])

        # MATCH DATE
        match_dates = []
        dates = soup.select('div[data-tab="scoring"] td.matchdate')
        for date in dates:
            match_dates.append(date.text)

        # ATTACK DATA    
        attack_kills, attack_faults, attack_shots = [], [], []
        attacks = soup.select('div[data-tab="attack"] tbody tr')
        for attack in attacks:
            attack_kills.append(attack.find('td', class_='attacks').text)
            attack_faults.append(attack.find('td', class_='faults').text)
            attack_shots.append(attack.find('td', class_='shots').text)

        # BLOCK DATA    
        block_kills, block_faults, block_rebounds = [], [], []
        blocks = soup.select('div[data-tab="block"] tbody tr')
        for block in blocks:
            block_kills.append(block.find('td', class_='stuff-blocks').text)
            block_faults.append(block.find('td', class_='faults').text)
            block_rebounds.append(block.find('td', class_='rebounds').text)

        # SERVE DATA    
        serve_aces, serve_errors, serve_attempts = [], [], []
        serves = soup.select('div[data-tab="serve"] tbody tr')
        for serve in serves:
            serve_aces.append(serve.find('td', class_='serve-points').text)
            serve_errors.append(serve.find('td', class_='faults').text)
            serve_attempts.append(serve.find('td', class_='hits').text)

        # RECEPTION DATA    
        rec_excellents, rec_faults, rec_attempts = [], [], []
        recs = soup.select('div[data-tab="reception"] tbody tr')
        for rec in recs:
            rec_excellents.append(rec.find('td', class_='excellents').text)
            rec_faults.append(rec.find('td', class_='faults').text)
            rec_attempts.append(rec.find('td', class_='serve-receptions').text)

        # DIG DATA    
        dig_excellents, dig_faults, dig_attempts = [], [], []
        digs = soup.select('div[data-tab="dig"] tbody tr')
        for dig in digs:
            dig_excellents.append(dig.find('td', class_='great-save').text)
            dig_faults.append(dig.find('td', class_='faults').text)
            dig_attempts.append(dig.find('td', class_='receptions').text)

        # SETTING DATA    
        set_excellents, set_faults, set_stills = [], [], []
        sets = soup.select('div[data-tab="set"] tbody tr')
        for set in sets:
            set_excellents.append(set.find('td', class_='running-sets').text)
            set_faults.append(set.find('td', class_='faults').text)
            set_stills.append(set.find('td', class_='still-sets').text)
            
        stats_df = pd.DataFrame.from_dict({
            'first_name' : [first_name] * len(opponents),
            'last_name' : [last_name] * len(opponents),
            'nationality' : [nationality] * len(opponents),
            'position': [position] * len(opponents),
            'opponent' : opponents,
            'match_date' : match_dates,
            'points_scored' : attack_kills + block_kills + serve_aces,
            'attack_kills' : attack_kills, 
            'attack_faults' : attack_faults,
            'attack_shots' : attack_shots,
            'block_kills' : block_kills,
            'block_faults' : block_faults,
            'block_rebounds' : block_rebounds,
            'serve_aces': serve_aces,
            'serve_errors' : serve_errors,
            'serve_attempts' : serve_attempts,
            'rec_excellents': rec_excellents,
            'rec_faults' : rec_faults,
            'rec_attempts' : rec_attempts,
            'dig_excellents' : dig_excellents, 
            'dig_faults' : dig_faults,
            'dig_attempts' : dig_attempts,
            'set_excellents' : set_excellents, 
            'set_faults' : set_faults,
            'set_stills' : set_stills
        })

        return bio_dict, stats_df
    
    except AttributeError as err:
        try:
            disclaimer = soup.find('div', class_='vbw-no-player-statistics-disclaimer')
            logging.warning(disclaimer.text)
            return None, None
        except:
            logging.error(f'Unknown Error - {url}' )
            return None, None

def main():
    logging.basicConfig(filename='player_bio_stats.log', encoding='utf-8', level=logging.INFO)
    
    divisions = ['Men', 'Women']
    
    for div in divisions:
    
        url = f'https://en.volleyballworld.com/volleyball/competitions/vnl-2022/teams/{div}/'
        logging.info(f'Started scraping from: {url}')
        print(f'Started scraping from: {url}')
        
        team_links = get_team_links(url)
        
        player_bio = []
        stats_df = pd.DataFrame()
        
        for team_link, country in team_links:
            logging.info(f'Started scraping team {country}')
            print(f'Started scraping team {country}')
            player_links = get_player_links(team_link)
            
            for player_link, player_name in player_links:
                logging.info(f'Getting data: {player_name}')
                print(f'Getting data: {player_name}')
                player_bio_list, player_stats_df = get_player_bio_stats(player_link)
                player_bio.append(player_bio_list)
                stats_df = pd.concat([stats_df, player_stats_df], ignore_index=True)
                time.sleep(1)

            time.sleep(3)
            
        player_bio = list(filter(None, player_bio))
        #RESEARCH: dataframe concat with None, personal code tests looks like concat ignores the None   
        
        bio_df = pd.DataFrame(player_bio)
        
        bio_df.to_csv(f'../data/raw/{div[0].lower()}_player_bios.csv', index=False)
        stats_df.to_csv(f'../data/raw/{div[0].lower()}_player_stats.csv', index=False)
    
if __name__ == '__main__':
   main()
