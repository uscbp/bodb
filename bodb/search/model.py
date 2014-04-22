import operator
from django.db.models import Q
from bodb.models import Document, Model
from bodb.search.document import DocumentWithLiteratureSearch
from registration.models import User
from taggit.utils import parse_tags

def runModelSearch(search_data, userId, exclude=None):
    filters=[]

    op=operator.or_
    if search_data['search_options']=='all':
        op=operator.and_

    # create Model search
    searcher=ModelSearch(search_data)

    # construct search query
    for key in search_data.iterkeys():
        # if the searcher can search by this field
        if hasattr(searcher, 'search_%s' % key):
            # add field to query
            dispatch=getattr(searcher, 'search_%s' % key)
            filters.append(dispatch(userId))

    # restrict to user's own entries or those of other users that are not drafts
    if User.objects.filter(id=userId):
        user=User.objects.get(id=userId)
    else:
        user=User.get_anonymous()

    q = reduce(op,filters) & Document.get_security_q(user)

    # get results
    if q and len(q):
        results = Model.objects.filter(q).select_related().distinct()
    else:
        results = Model.objects.all().select_related()

    if exclude is not None and not exclude=='None':
        results=results.exclude(id=int(exclude))

    return results.order_by('title')


class ModelSearch(DocumentWithLiteratureSearch):

    def search_author(self, userId):
        if self.author:
            op=operator.or_
            if self.author_options=='all':
                op=operator.and_
            words=parse_tags(self.author)
            keyword_filters=[Q(Q(authors__author__first_name__icontains=word) | Q(authors__author__last_name__icontains=word)) for word in words]
            return reduce(op,keyword_filters)
        return Q()

    # search by building SED
    def search_building_sed(self, userId):
        if self.building_sed:
            op=operator.or_
            if self.building_sed_options=='all':
                op=operator.and_
            words=parse_tags(self.building_sed)
            title_filters=[Q(related_build_sed_document__sed__title__icontains=word) for word in words]
            description_filters=[Q(related_build_sed_document__sed__brief_description__icontains=word) for word in words]
            narrative_filters=[Q(related_build_sed_document__sed__narrative__icontains=word) for word in words]
            relevance_filters=[Q(related_build_sed_document__relevance_narrative__icontains=word) for word in words]
            keyword_q = reduce(op,title_filters) | reduce(op,description_filters) | reduce(op,narrative_filters) | \
                        reduce(op,relevance_filters)
            return keyword_q
        return Q()

    # search by testing SED
    def search_testing_sed(self, userId):
        if self.testing_sed:
            op=operator.or_
            if self.testing_sed_options=='all':
                op=operator.and_
            words=parse_tags(self.testing_sed)
            title_filters=[Q(related_test_sed_document__sed__title__icontains=word) for word in words]
            description_filters=[Q(related_test_sed_document__sed__brief_description__icontains=word) for word in words]
            narrative_filters=[Q(related_test_sed_document__sed__narrative__icontains=word) for word in words]
            keyword_q = reduce(op,title_filters) | reduce(op,description_filters) | reduce(op,narrative_filters)
            return keyword_q
        return Q()

    # search by Prediction
    def search_prediction(self, userId):
        if self.prediction:
            op=operator.or_
            if self.prediction_options=='all':
                op=operator.and_
            words=parse_tags(self.prediction)
            title_filters=[Q(prediction__title__icontains=word) for word in words]
            description_filters=[Q(prediction__brief_description__icontains=word) for word in words]
            narrative_filters=[Q(prediction__narrative__icontains=word) for word in words]
            keyword_q = reduce(op,title_filters) | reduce(op,description_filters) | reduce(op,narrative_filters)
            return keyword_q
        return Q()

    # search by SSR
    def search_ssr(self, userId):
        if self.ssr:
            op=operator.or_
            if self.ssr_options=='all':
                op=operator.and_
            words=parse_tags(self.ssr)
            title_filters=[Q(Q(related_test_sed_document__testsedssr__ssr__title__icontains=word) |\
                             Q(prediction__predictionssr__ssr__title__icontains=word)) for word in words]
            description_filters=[Q(Q(related_test_sed_document__testsedssr__ssr__brief_description__icontains=word) |\
                                   Q(prediction__predictionssr__ssr__brief_description__icontains=word)) for word in words]
            narrative_filters=[Q(Q(related_test_sed_document__testsedssr__ssr__narrative__icontains=word) |\
                                 Q(prediction__predictionssr__ssr__narrative__icontains=word)) for word in words]
            keyword_q = reduce(op,title_filters) | reduce(op,description_filters) | reduce(op,narrative_filters)
            return keyword_q
        return Q()

