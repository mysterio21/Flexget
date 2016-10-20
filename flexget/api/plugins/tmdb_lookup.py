from __future__ import unicode_literals, division, absolute_import

from flask import jsonify

from flexget.api import api, APIResource
from flexget.api.app import etag, BadRequest, NotFoundError
from flexget.plugin import get_plugin_by_name

tmdb_api = api.namespace('tmdb', description='TMDB lookup endpoint')


class ObjectsContainer(object):
    poster_object = {
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'movie_id': {'type': 'integer'},
            'url': {'type': 'integer', 'format': 'uri'},
            'file_path': {'type': 'string'},
            'width': {'type': 'integer'},
            'height': {'type': 'integer'},
            'aspect_ratio': {'type': 'number'},
            'vote_average': {'type': 'number'},
            'vote_count': {'type': 'integer'},
            'language': {'type': 'string'}
        },
        'required': ['id', 'movie_id', 'url', 'file_path', 'width', 'height', 'aspect_ratio', 'vote_average',
                     'vote_count', 'language'],
        'additionalProperties': False
    }
    movie_object = {
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'imdb_id': {'type': 'string'},
            'url': {'type': ['integer', 'null'], 'format': 'uri'},
            'name': {'type': 'string'},
            'original_name': {'type': ['string', 'null']},
            'alternative_name': {'type': ['string', 'null']},
            'year': {'type': 'integer'},
            'certification': {'type': ['string', 'null']},
            'runtime': {'type': 'integer'},
            'language': {'type': 'string'},
            'overview': {'type': 'string'},
            'tagline': {'type': 'string'},
            'rating': {'type': ['number', 'null']},
            'votes': {'type': ['integer', 'null']},
            'popularity': {'type': ['integer', 'null']},
            'adult': {'type': 'boolean'},
            'budget': {'type': ['integer', 'null']},
            'revenue': {'type': ['integer', 'null']},
            'homepage': {'type': ['integer', 'null'], 'format': 'uri'},
            'posters': {'type': 'array', 'items': poster_object},
            'genres': {'type': 'array', 'items': {'type': 'string'}},
            'updated': {'type': 'string', 'format': 'date-time'},
        },
        'required': ['id', 'match', 'name', 'url', 'year', 'original_name', 'alternative_name', 'certification',
                     'runtime', 'language', 'overview', 'tagline', 'rating', 'votes', 'popularity', 'adult', 'budget',
                     'revenue', 'homepage', 'posters', 'genres', 'updated'],
        'additionalProperties': False
    }


description = 'Either title, TMDB ID or IMDB ID are required for a lookup'

return_schema = api.schema('tmdb_search_schema', ObjectsContainer.movie_object)

tmdb_parser = api.parser()
tmdb_parser.add_argument('title', help='Movie title')
tmdb_parser.add_argument('tmdb_id', help='TMDB ID')
tmdb_parser.add_argument('imdb_id', help='IMDB ID')
tmdb_parser.add_argument('year', type=int, help='Movie year')
tmdb_parser.add_argument('only_cached', type=int, help='Return only cached results')


@tmdb_api.route('/movies/')
@api.doc(description=description)
class TMDBMoviesAPI(APIResource):
    @etag
    @api.response(200, model=return_schema)
    @api.response(NotFoundError)
    @api.response(BadRequest)
    @api.doc(parser=tmdb_parser)
    def get(self, session=None):
        """ Get TMDB movie data """
        args = tmdb_parser.parse_args()
        title = args.get('title')
        tmdb_id = args.get('tmdb_id')
        imdb_id = args.get('imdb_id')

        if not (title or tmdb_id or imdb_id):
            raise BadRequest(description)

        lookup = get_plugin_by_name('api_tmdb').instance.lookup
        try:
            movie = lookup(session=session, **args)
        except LookupError as e:
            raise NotFoundError(e.args[0])
        return jsonify(movie.to_dict())
