import * as React from "react"
import { Button, createStyles, Link, Typography, WithStyles, withStyles } from "@material-ui/core"
import Grid from "@material-ui/core/Grid"
import Checkbox from "@material-ui/core/Checkbox"
import FormControlLabel from "@material-ui/core/FormControlLabel"
import AlternateLinks from "../alternate_links"
import { NewsItem } from "../../news_room_api/news_item_api"
import { StarBorderRounded } from "@material-ui/icons"
import { Api } from "../../Api"
import { withAuthHandling, WithAuthHandling } from "../../WithAuthHandling"
import { RouteComponentProps } from "react-router"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { withRouter } from "react-router-dom"
import { UpsertSavedNewsItemResponse } from "../../news_room_api/saved_news_api"
import { MarkAsReadItem, ScrollableItem } from "../scrollable_items"

const styles = createStyles({
    header: {
        fontWeight: "bold",
    },
    card: {
        marginBottom: "2px",
        backgroundColor: "#efefef",
        justifyContent: "left",
        padding: "10px",
    },
    cardRead: {
        marginBottom: "2px",
        backgroundColor: "#afafaf",
        justifyContent: "left",
        padding: "10px",
        opacity: ".6",
    },
    cardDescription: {
        paddingTop: "7px",
    },
    cardTitle: {
        paddingTop: "3px",
        paddingBottom: "4px",
    },
    titleLink: {
        "&:visited": {
            color: "#c39ea4",
            fontSize: "smaller",
        },
        fontSize: "large",
    },
    domainIcon: {
        height: 20,
        verticalAlign: "middle",
        paddingRight: 4,
    },

    itemControlBar: {},
    savedIcon: {
        color: "orange",
    },
    notSavedIcon: {},
})

interface NewsItemViewProps
    extends WithAuthHandling,
        RouteComponentProps,
        WithSnackbarProps,
        WithStyles<typeof styles> {
    news_item: NewsItem
    register_scrollable_item: (scrollable_item: ScrollableItem) => void
    register_mark_as_read_item?: (mark_as_read_item: MarkAsReadItem) => void
}

interface NewsItemViewState {
    is_read: boolean
    is_saved: boolean
    saved_news_item_id: string | null
    news_item: NewsItem
    keep_unread: boolean
}

class NewsItemView extends React.Component<NewsItemViewProps> implements ScrollableItem, MarkAsReadItem {
    element: Element | null = null
    state: NewsItemViewState = {
        is_read: false,
        keep_unread: false,
        is_saved: false,
        saved_news_item_id: this.props.news_item.saved_news_item_id,
        news_item: this.props.news_item,
    }

    api: Api

    constructor(props: NewsItemViewProps) {
        super(props)
        this.api = new Api(this.props)
        this.props.register_scrollable_item(this)
        if (this.props.register_mark_as_read_item) {
            this.props.register_mark_as_read_item(this)
        }
    }

    componentDidMount(): void {
        this.setState({
            is_saved: this.props.news_item.is_saved,
            is_read: this.props.news_item.is_read,
            news_item: this.props.news_item,
        })
    }

    /**********
     * MarkAsReadItem methods
     **********/
    must_be_marked_as_read(): MarkAsReadItem | null {
        if (this.state.is_read || this.state.keep_unread) {
            return null
        }
        if (this.scrolled_out_of_view()) {
            return this
        }
        return null
    }

    confirm_marked_as_read(): void {
        this.props.news_item.is_read = true
        this.setState({ is_read: true })
    }

    item_id(): string {
        return this.props.news_item._id
    }

    /**********
     * ScrollableItem methods
     ***********/
    reportYPosition(): number {
        return this.element?.getBoundingClientRect().y || -1
    }

    scroll_to_top(): void {
        this.element?.scrollIntoView()
    }

    open_item(): void {
        document.open(this.props.news_item.link, "_blank", "noopener")
    }

    scrolled_out_of_view(): boolean {
        if (this.element) {
            return this.element.getBoundingClientRect().bottom < 150
        }
        return false
    }

    toggle_saved_item(): void {
        if (this.props.news_item.is_saved) {
            this.api
                .delete(`/saved-news/${this.state.saved_news_item_id}`, JSON.stringify({}))
                .catch((reason) => console.error(reason))
        } else {
            this.api
                .post<UpsertSavedNewsItemResponse>(
                    "/saved-news",
                    JSON.stringify({ news_item_id: this.props.news_item._id })
                )
                .then((response) => this.setState({ saved_news_item_id: response[1].saved_news_item_id }))
                .catch((reason) => console.error(reason))
        }

        this.props.news_item.is_saved = !this.props.news_item.is_saved
        this.setState({ is_saved: !this.state.is_saved })
    }

    render(): JSX.Element {
        const { classes } = this.props
        const news_item = this.props.news_item
        const url = new URL(news_item.link)
        const domain = url.hostname
        return (
            <Grid
                container
                className={this.state.is_read ? classes.cardRead : classes.card}
                ref={(t): void => {
                    this.element = t
                }}
            >
                <Grid item xs={12} className={classes.cardTitle}>
                    <Link href={news_item.link} className={classes.titleLink} target="_blank" rel="noopener">
                        <img src={news_item.favicon} className={classes.domainIcon} alt={`[${domain}]`} />
                        {news_item.title}
                    </Link>
                </Grid>
                <Grid item xs={12} className={classes.cardDescription}>
                    <div dangerouslySetInnerHTML={{ __html: news_item.description }} />
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="subtitle2">
                        {news_item.feed_title} / {news_item.published}
                    </Typography>
                </Grid>
                <Grid item md={4} xs={12} className={classes.itemControlBar}>
                    <Button size="small" variant="text" onClick={(): void => this.toggle_saved_item()}>
                        <StarBorderRounded className={this.state.is_saved ? classes.savedIcon : classes.notSavedIcon} />
                    </Button>
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={this.state.keep_unread}
                                onChange={(): void => {
                                    this.setState({ keep_unread: !this.state.keep_unread })
                                }}
                                name="keep_unread"
                                color="primary"
                            />
                        }
                        label="Keep unread"
                    />
                </Grid>
                <Grid item md={8} xs={12}>
                    <AlternateLinks
                        alternate_links={news_item.alternate_links}
                        alternate_title_links={news_item.alternate_title_links}
                        alternate_favicons={news_item.alternate_favicons}
                    />
                </Grid>
                <div />
            </Grid>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(NewsItemView))))
