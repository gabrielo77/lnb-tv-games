# -*- coding: utf-8 -*-

##############################################################################
#
#    LNB Tv Games - Get Argentine's Liga Nacional de Basquetbol games that
#    will be on tv and when. Copyright (C) 2015 Gabriel Davini
#
#    This file is a part of LNB Tv Games
#
#    LNB Tv Games is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    LNB Tv Games is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from __future__ import print_function

import re
from datetime import datetime

import requests  # fades.pypi
from bs4 import BeautifulSoup  # fades.pypi beautifulsoup4==4.3.2


class Game(object):

    def __init__(self, local, visitor, datetime, channel):
        """docstring for __init__"""
        self.local = local
        self.visitor = visitor
        self.datetime = datetime
        self.channel = channel
        self.repr_format = ("%(local)s vs. %(visitor)s on %(local_date)s on channel %(channel)s")

    def __getitem__(self, key):
        """docstring for __getitem___"""
        return getattr(self, key)

    def __repr__(self):
        """docstring for __repr__"""
        return self.repr_format % self

    @property
    def minute(self):
        """docstring for minute"""
        return self.datetime.minute

    @property
    def hour(self):
        """docstring for hour"""
        return self.datetime.hour

    @property
    def year(self):
        """docstring for year"""
        return self.datetime.year

    @property
    def month(self):
        """docstring for year"""
        return self.datetime.strftime("%B")

    @property
    def daynumber(self):
        """docstring for year"""
        return self.datetime.day

    @property
    def day(self):
        """docstring for year"""
        return self.datetime.strftime("%A")

    @property
    def local_date(self):
        """docstring for local_date"""
        return self.datetime.strftime("%c")


class GamesPool(object):

    def __init__(self, url, normalize_names=True):
        """docstring for __init__"""
        self.url = url
        try:
            self.request = requests.get(url)
        except Exception as exc:
            print(exc)
            raise
        self.soup = BeautifulSoup(self.request.text)
        self._games = set()
        self._find_games(normalize_names)

    @property
    def games(self):
        """docstring for get_games"""
        return self._games

    def _normalize_team_name(self, team):
        """docstring for _normalize_team_name"""
        names = team.split()
        if len(names) > 1:
            res = []
            for name in names:
                match = re.match("\(.+\)", name)
                if match:
                    res.append(name)
                else:
                    res.append(name.capitalize())
            return " ".join(res).strip()
        else:
            return team.capitalize().strip()

    def _find_games(self, normalize_names=True):
        """docstring for _find_games"""
        for div in self.soup.find_all("div"):
            div_class = div.get("class")
            if div_class and len(div_class) > 1 and 'televisados' in div_class:
                h4s = div.div.div.find_all("h4")
                ps = div.div.div.find_all("p")
                for h in range(len(h4s)):
                    teams = h4s[h].get_text()
                    split = filter(None, re.split("^(.+)\s+vs\.?\s+(.+)$", teams, flags=re.I))
                    local, visitor = split
                    if normalize_names:
                        local = self._normalize_team_name(local)
                        visitor = self._normalize_team_name(visitor)
                    text = ps[h].get_text()
                    m = re.match("""
                                 ^(?P<date_time>  # date_time class with date and time splited
                                 (?P<date>(?:\d{1,2}\/){2}\d{2,4})
                                 \s
                                 (?P<time>\d{1,2}\:\d{1,2}))\s+[hH]s[tTvV\.\s]*
                                 \s
                                 (?P<channel>.+)$  # channel class
                                 """, text, flags=re.X)
                    d = m.groupdict()
                    date_time = datetime.strptime("%(date_time)s" % d, "%d/%m/%Y %H:%M")
                    new_game = Game(local, visitor, date_time, d["channel"])
                    self._games.add(new_game)
                self._games = sorted(self._games, key=lambda g: g.datetime)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument("-d", "--date", help="Select specific date DATE.",
                        type=lambda d: datetime.strptime(d, "%d/%m/%Y"))
    parser.add_argument("-U", "--user-agent", help="Identify as USER-AGENT to the HTTP server.")
    # parser.add_argument("", "", help="")

    options = parser.parse_args()
    print(options.date)

    url = "http://www.lnb.com.ar"
    gp = GamesPool(url)
    for game in gp.games:
        print(game)
