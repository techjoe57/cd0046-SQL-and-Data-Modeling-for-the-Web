#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import date
from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Implemented Venue model and completed all model relationships and properties as a database migration

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, server_default="false")
    seeking_description = db.Column(db.String(250), nullable=True)
    shows = db.relationship('Show', backref='listVenues', lazy='dynamic')

    def __repr__(self) -> str:
      return f'<Venue {self.id} {self.name} {self.genres} {self.city} {self.state} {self.address}>'

# Implemented Artist model and completed all model relationships and properties as a database migration

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, server_default="false")
    seeking_description = db.Column(db.String(250), nullable=True)
    shows = db.relationship('Show', backref='listArtists', lazy='dynamic')

    def __repr__(self) -> str:
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.genres}>'


# Implemented Show model and completed all model relationships and properties as a database migration

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, default=datetime.utcnow)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

  def __repr__(self) -> str:
      return f'<Show id: {self.id},artist_id: {self.artist_id},venue_id: {self.venue_id} {self.start_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
# Venues populated by real data
def venues():
  data =[]
  venue_locations =Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  for (city, state) in venue_locations:
    venues = Venue.query.filter_by(state=state, city=city).all()
    data.append({
      'city': city,
      'state': state,
      'venues': venues
    })

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

  # An implemented search on artists with partial string search. 

  response= {}
  venues=[]
  search_term = request.form.get('search_term', '').lower()
  search_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  for venue in search_result:
    venue_shows_count = Show.query.join(Venue).filter(Venue.id == venue.id).count()

    venues.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': venue_shows_count
    })

    response['count'] = len(search_result)
    response['data'] = venues
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  # shows the venue page populated with real data
  
  past_shows = []
  upcoming_shows = []

  venue = Venue.query.filter_by(id=venue_id).first()
  venue_shows = Show.query.join(Venue).filter(Venue.id == venue_id).all()
  print ('Venue Shows: ',venue_shows)

  for show in filter(lambda show: show.start_time.date() < date.today(), venue_shows):
    artist = Artist.query.filter_by(id=show.artist_id).first()
    past_shows.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(show.start_time)
    })

  for show in filter(lambda show: show.start_time.date() < date.today(), venue_shows):
    artist = Artist.query.filter_by(id=show.artist_id).first()
    upcoming_shows.append({
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': str(show.start_time)
    })

   

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)

  }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'crsf':False})

  if form.validate():
    try:
      venue = Venue(
        name = form.name.data,
        state = form.state.data,
        city = form.city.data,
        phone = form.phone.data,
                address = form.address.data,
                genres = form.genres.data,
                image_link = form.image_link.data,
                facebook_link = form.facebook_link.data,
                seeking_talent = form.seeking_talent.data,
                website_link = form.website_link.data,
                seeking_description = form.seeking_description.data

      )
      
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/venues.html')
    except ValueError as e:
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed!')
            print(e)  
    finally:
      db.session.close()
  
  else:
      message = []
      for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
      flash('Errors ' + str(message))
      return render_template('forms/new_venue.html', form=form)
  return render_template('pages/venues.html')
    

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.order_by(Artist.id.asc()).all()
  return render_template('pages/artists.html', artists=artists)
 

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_item', '')
  results = db.session.query(Artist).\
  filter(Artist.name.ilike('%'+ search_term + '%')).all()

  response={
    'count': len(results),
    'data': results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    temp_show = {
        'venue_id': show.venue_id,
        'venue_name': show.listVenues.name,
        'venue_image_link': show.listVenues.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)
 
  data={
     "id" : artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "upcoming_shows_count": len(upcoming_shows),
    "past_shows_count": len(past_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id==artist_id).first()
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form, meta={'csrf':False})

  if form.validate():
    try:
      artist = {
        "name": form.name.data,
        "city": form.city.data,
        "state": form.state.data,
        "phone": form.phone.data,
        "genres": form.genres.data,
        "image_link": form.image_link.data,
        "facebook_link": form.facebook_link.data,
        "seeking_venue": form.seeking_venue.data,
        "website_link": form.website_link.data,
        "seeking_description": form.seeking_description.data,
      }
      Artist.query.filter_by(id=artist_id).update(artist)
      db.session.commit()
      flash('Artist: ' + request.form['name'] + ' was successfully updated!')
    except ValueError as e:
      db.session.rollback()
      flash('Artist: ' + request.form['name'] + ' was not successfully updated!')
      print(e)
    finally:
        db.session.close()
  else:
        for error in form.errors:
            flash(form.errors[error][0])
        return redirect(url_for('edit_artist', artist_id=artist_id))
        
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter(Venue.id==venue_id).first()
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form , meta={'csrf': False})

  if form.validate():
      try:
        venue = {
        "name": form.name.data,
        "city": form.city.data,
        "state": form.state.data,
        "phone": form.phone.data,
        "address": form.address.data,
        "genres": form.genres.data,
        "image_link": form.image_link.data,
        "facebook_link": form.facebook_link.data,
        "seeking_talent": form.seeking_talent.data,
        "website_link": form.website_link.data,
        "seeking_description": form.seeking_description.data,
      }

        Venue.query.filter_by(id=venue_id).update(venue)
        db.session.commit()
        flash('Venue: ' + request.form['name'] + ' was successfully updated')
      except Exception as e:
        db.session.rollback()
        error = True
        print(f'Error ==> {e}')
        flash('Venue: ' + request.form['name'] + ' was not successfully updated')
      finally:
        db.session.close()
  else: 
      for error in form.errors:
        flash(form.errors[error][0])
      return redirect(url_for('edit_venue', venue_id=venue_id))
        
  return redirect(url_for('show_venue', venue_id=venue_id))

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf':False})
   # on successful db insert, flashes success
  if form.validate():
    try:
            artist = Artist(
                name  = form.name.data,
                city  = form.city.data,
                state = form.state.data,
                phone = form.phone.data,
                genres = form.genres.data,
                image_link = form.image_link.data,
                facebook_link = form.facebook_link.data,
                seeking_venue = form.seeking_venue.data,
                website_link = form.website_link.data,
                seeking_description = form.seeking_description.data)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/artists.html')

  # on unsuccessful db insert, flashes an error 
    except ValueError as e:
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            print(e)
    finally:
            db.session.close()
  else:
      message = []
      for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
      flash('Errors ' + str(message))

      return render_template('forms/new_artist.html', form=form)
  return render_template('pages/artists.html')
      
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows (real venues data)
  data=[]
  shows = Show.query.order_by(Show.start_time.desc()).all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data.extend([{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }])
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # on successful db insert, flashes success
  form = ShowForm(request.form,meta={'csrf':False})
  error = False
  if form.validate():
    try:
      show = Show(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data
      )
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')

# on unsuccessful db insert, flashes an error instead.
    except Exception as e:
      db.session.rollback()
      error = True
      flash('An error occurred. Show could not be listed.')
      print(e)
    finally:
      db.session.close()
  else:
    for error in form.errors:
      flash(form.errors[error][0])
    return render_template('forms/new_show.html', form=form)
  return render_template('pages/shows.html')

  # called to create new shows in the db, upon submitting new show listing form
  # inserts form data as a new Show record in the db, instead

  
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
