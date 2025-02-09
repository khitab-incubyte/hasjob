from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import CheckboxInput, ListWidget

from baseframe import __
from coaster.utils import getbool
import baseframe.forms as forms

from ..models import (
    BANNER_LOCATION,
    CAMPAIGN_ACTION,
    CAMPAIGN_POSITION,
    Board,
    Campaign,
)
from .helper import content_css, optional_url


class CampaignContentForm(forms.Form):
    subject = forms.StringField(
        __("Subject"),
        description=__("A subject title shown to viewers"),
        validators=[forms.validators.Optional()],
        filters=[forms.filters.strip(), forms.filters.none_if_empty()],
    )
    blurb = forms.TinyMce4Field(
        __("Blurb"),
        description=__(
            "Teaser to introduce the campaign and convince users to interact"
        ),
        content_css=content_css,
        validators=[forms.validators.Optional(), forms.validators.AllUrlsValid()],
    )
    description = forms.TinyMce4Field(
        __("Description"),
        description=__("Optional additional content to follow after the blurb"),
        content_css=content_css,
        validators=[forms.validators.Optional(), forms.validators.AllUrlsValid()],
    )
    banner_image = forms.URLField(
        __("Banner image URL"),
        validators=[forms.validators.Optional()],  # TODO: Use ImgeeField
        description=__("An image to illustrate your campaign"),
    )
    banner_location = forms.RadioField(
        __("Banner location"),
        choices=list(BANNER_LOCATION.items()),
        coerce=int,
        description=__("Where should this banner appear relative to text?"),
    )


class CampaignForm(forms.Form):
    title = forms.StringField(
        __("Title"),
        description=__("A reference name for looking up this campaign again"),
        validators=[forms.validators.DataRequired(__("A title is required"))],
        filters=[forms.filters.strip()],
    )
    start_at = forms.DateTimeField(__("Start at"), naive=False)
    end_at = forms.DateTimeField(
        __("End at"),
        validators=[
            forms.validators.GreaterThan(
                'start_at', __("The campaign can’t end before it starts")
            )
        ],
        naive=False,
    )
    public = forms.BooleanField(__("This campaign is live"))
    position = forms.RadioField(
        __("Display position"), choices=list(CAMPAIGN_POSITION.items()), coerce=int
    )
    priority = forms.IntegerField(
        __("Priority"),
        default=0,
        description=__(
            "A larger number is higher priority when multiple campaigns are running on the "
            "same dates. 0 implies lowest priority"
        ),
    )
    boards = QuerySelectMultipleField(
        __("Boards"),
        widget=ListWidget(),
        option_widget=CheckboxInput(),
        query_factory=lambda: Board.query.order_by(Board.featured.desc(), Board.title),
        get_label='title_and_name',
        validators=[forms.validators.Optional()],
        description=__("Select the boards this campaign is active on"),
    )
    geonameids = forms.GeonameSelectMultiField(
        "Locations",
        description=__(
            "This campaign will be targeted at users and jobs with matching locations"
        ),
    )
    user_required = forms.RadioField(
        __("User is required"),
        coerce=getbool,
        choices=[
            (None, __("N/A – Don’t target by login status")),
            (True, __("Yes – Show to logged in users only")),
            (False, __("No – Show to anonymous users only")),
        ],
    )
    flags = forms.RadioMatrixField(
        "Flags",
        coerce=getbool,
        fields=Campaign.flag_choices,
        description=__(
            "All selected flags must match the logged in user for the campaign to be shown"
        ),
        choices=[('None', __("N/A")), ('True', __("True")), ('False', __("False"))],
    )
    content = forms.FormField(CampaignContentForm, __("Campaign content"))

    def validate_geonameids(self, field):
        field.data = [int(x) for x in field.data if x.isdigit()]


class CampaignActionForm(forms.Form):
    title = forms.StringField(
        __("Title"),
        description=__("Contents of the call to action button"),
        validators=[forms.validators.DataRequired("You must provide some text")],
        filters=[forms.filters.strip()],
    )
    icon = forms.StringField(
        __("Icon"),
        validators=[forms.validators.Optional()],
        filters=[forms.filters.none_if_empty()],
        description=__("Optional Font-Awesome icon name"),
    )
    public = forms.BooleanField(__("This action is live"))
    type = forms.RadioField(  # noqa: A003
        __("Type"),
        choices=list(CAMPAIGN_ACTION.items()),
        validators=[forms.validators.DataRequired(__("This is required"))],
    )
    group = forms.StringField(
        __("RSVP group"),
        validators=[forms.validators.Optional()],
        filters=[forms.filters.none_if_empty()],
        description=__("If you have multiple RSVP actions, add an optional group name"),
    )
    category = forms.RadioField(
        __("Category"),
        validators=[forms.validators.DataRequired(__("This is required"))],
        widget=forms.InlineListWidget(class_='button-bar', class_prefix='btn btn-'),
        choices=[
            ('default', __("Default")),
            ('primary', __("Primary")),
            ('success', __("Success")),
            ('info', __("Info")),
            ('warning', __("Warning")),
            ('danger', __("Danger")),
        ],
    )
    message = forms.TinyMce4Field(
        __("Message"),
        description=__(
            "Message shown after the user has performed an action (for forms and RSVP type)"
        ),
        content_css=content_css,
        validators=[forms.validators.Optional(), forms.validators.AllUrlsValid()],
    )
    link = forms.URLField(
        __("Link"),
        description=__("URL to redirect to, if type is “follow link”"),
        validators=[
            optional_url,
            forms.validators.Length(
                min=0, max=250, message=__("%%(max)d characters maximum")
            ),
            forms.validators.ValidUrl(),
        ],
        filters=[forms.filters.strip()],
    )
    form = forms.TextAreaField(
        __("Form JSON"),
        description=__("Form definition (for form type)"),
        validators=[forms.validators.Optional()],
    )
    seq = forms.IntegerField(
        __("Sequence #"),
        validators=[forms.validators.DataRequired(__("This is required"))],
        description=__(
            "Sequence number for displaying this action when multiple actions are available to the user"
        ),
    )
