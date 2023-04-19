#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime as dt
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database
datetime_format = "%Y-%m-%d"
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Area:
  def __init__(self, city, state, venues):
    self.city = city
    self.state = state
    self.venues = venues
class Venue_Show:
  def __init__(self, venue_name, venue_image_link, start_time):
    self.venue_name = venue_name
    self.venue_image_link = venue_image_link
    self.start_time = start_time
class Artist_Show:
  def __init__(self, artist_name, artist_image_link, start_time):
    self.artist_name = artist_name
    self.artist_image_link = artist_image_link
    self.start_time = start_time

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    created_time = db.Column(db.DateTime, nullable=True, default=datetime.now())

    Shows = db.relationship('Show', backref='Venue', lazy=True)
    upcoming_shows = []
    past_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0

    def set_upcomming_and_past_shows(self):
      current_date = dt.datetime.now()
      self.upcoming_shows.clear()
      self.past_shows.clear()
      for s in self.Shows:
        up_show = Artist_Show(s.Artist.name, s.Artist.image_link, s.start_time)
        if (current_date > s.start_time):
          self.past_shows.append(up_show)
        else:
          self.upcoming_shows.append(up_show)
      self.past_shows_count = len(self.past_shows)
      self.upcoming_shows_count = len(self.upcoming_shows)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    created_time = db.Column(db.DateTime, nullable=True, default=datetime.now())

    Shows = db.relationship('Show', backref='Artist', lazy=False)

    upcoming_shows = []
    past_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0

    def set_upcomming_and_past_shows(self):
      current_date = dt.datetime.now()
      self.upcoming_shows.clear()
      self.past_shows.clear()
      for s in self.Shows:
        up_show = Venue_Show(s.Venue.name, s.Venue.image_link, s.start_time)
        if (current_date > s.start_time):
          self.past_shows.append(up_show)
        else:
          self.upcoming_shows.append(up_show)
      self.past_shows_count = len(self.past_shows)
      self.upcoming_shows_count = len(self.upcoming_shows)

class Show(db.Model):
    __tablename__ = 'Show'
    
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True, default=datetime.now())
    created_time = db.Column(db.DateTime, nullable=True, default=datetime.now())


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
# app.app_context().push()
# db.create_all()
def format_datetime(value, format='medium'):
  date = value
  if isinstance(date, str):
    date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
  artists = Artist.query.order_by(Artist.created_time.desc()).limit(4).all()
  venues = Venue.query.order_by(Venue.created_time.desc()).limit(4).all()
  return render_template('pages/home.html', artists=artists, venues=venues)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venue_group = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state)
  areas = []
  for g in venue_group:
    venues = Venue.query.filter_by(city=g.city, state=g.state).all()
    area = Area(g.city, g.state, venues)
    areas.append(area)
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  venues = Venue.query.filter(Venue.name.ilike(search)).all()
  if len(venues) == 0: # if can not find with venue's name, then search with venue's city
    venues = Venue.query.filter(Venue.city.ilike(search)).all()

  response={
    "count": len(venues),
    "data": []
  }
  for v in venues:
    v.set_upcomming_and_past_shows()
    response['data'].append(v)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue:
    venue.genres= list(venue.genres.split(','))
    venue.set_upcomming_and_past_shows()
  else:
    flash('Not found the Venue Id ' + str(venue_id) + ' from out data')
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate():   
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, 
                    image_link=form.image_link.data, 
                    genres=str(form.genres.data).replace('{', '').replace('}','').replace('[', '').replace(']','').replace("'",""), 
                    facebook_link=form.facebook_link.data, website_link=form.website_link.data, seeking_talent=form.seeking_talent.data, 
                    seeking_description=form.seeking_description.data)
    try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      flash('Venue ' + request.form['name'] + ' was unsuccessfully insert into DB!')
      db.session.rollback()
    finally:
      db.session.close()

  else:
    flash('Venue ' + request.form['name'] + ' was unsuccessfully listed!')
    return render_template('forms/new_venue.html', form=form)

  return redirect(url_for('index'))
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  if form.validate(): 
    venue = Venue.query.get(venue_id)
    venue.name=form.name.data  
    venue.city=form.city.data
    venue.state=form.state.data
    venue.address=form.address.data
    venue.phone=form.phone.data
    venue.image_link=form.image_link.data, 
    venue.genres=str(form.genres.data).replace('{', '').replace('}','').replace('[', '').replace(']','').replace("'",""), 
    venue.facebook_link=form.facebook_link.data
    venue.website_link=form.website_link.data
    venue.seeking_talent=form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data

    try:
      db.session.commit()
      flash('venue ' + request.form['name'] + ' was successfully listed!')
    except:
      flash('venue ' + request.form['name'] + ' was unsuccessfully insert into DB!')
      db.session.rollback()
    finally:
      db.session.close()

  else:
    flash('venue ' + request.form['name'] + ' was unsuccessfully listed!')
    return render_template('forms/edit_venue.html', form=form)

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search = "%{}%".format(search_term)
  artists = Artist.query.filter(Artist.name.ilike(search)).all()
  if len(artists) == 0: # if can not find with Artist's name, then search with Artist's city
    artists = Artist.query.filter(Artist.city.ilike(search)).all()

  response={
    "count": len(artists),
    "data": []
  }
  for v in artists:
    v.set_upcomming_and_past_shows()
    response['data'].append(v)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    artist.genres= list(artist.genres.split(','))
    artist.set_upcomming_and_past_shows()
  else:
    flash('Not found the Artist Id ' + str(artist_id) + ' from out data')

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  if form.validate():
    artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, image_link=form.image_link.data, 
                    genres=str(form.genres.data).replace('{', '').replace('}','').replace('[', '').replace(']','').replace("'",""), 
                    facebook_link=form.facebook_link.data, website_link=form.website_link.data, seeking_venue=form.seeking_venue.data, 
                    seeking_description=form.seeking_description.data)
    try:
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      flash('Artist ' + request.form['name'] + ' was unsuccessfully insert into DB!')
      db.session.rollback()
    finally:
      db.session.close()

  else:
    flash('Artist ' + request.form['name'] + ' was unsuccessfully listed!')
    return render_template('forms/new_artist.html', form=form)
  return redirect(url_for('index'))
  #return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if form.validate(): 
    artist = Artist.query.get(artist_id)
    artist.name=form.name.data  
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.image_link=form.image_link.data, 
    artist.genres=str(form.genres.data).replace('{', '').replace('}','').replace('[', '').replace(']','').replace("'",""), 
    artist.facebook_link=form.facebook_link.data
    artist.website_link=form.website_link.data
    artist.seeking_venue=form.seeking_venue.data
    artist.seeking_description=form.seeking_description.data

    try:
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      flash('Artist ' + request.form['name'] + ' was unsuccessfully insert into DB!')
      db.session.rollback()
    finally:
      db.session.close()

  else:
    flash('Artist ' + request.form['name'] + ' was unsuccessfully listed!')
    return render_template('forms/edit_artist.html', form=form)

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  shows = Show.query.all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = ''
  form = ShowForm(request.form)
  if not form.validate():
    error = 'the input form invalide, please check!'
  else:
    artist = Artist.query.get(form.artist_id.data)
    venue = Venue.query.get(form.venue_id.data)
    if artist and venue:
      s = Show(Artist=artist, Venue=venue, start_time=form.start_time.data)
      try:
        db.session.add(s)
        db.session.commit()
      except:
        error='Error when try to insert a Show into DB'
        db.session.rollback()
      finally:
        db.session.close()
    else:
      error = 'Could not find Artist or Venue in Database'

  if error != '':
    flash(error);
    return render_template('forms/new_show.html', form=form)
  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
