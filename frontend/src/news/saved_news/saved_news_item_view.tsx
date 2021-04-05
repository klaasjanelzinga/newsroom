import { RouteComponentProps, withRouter } from "react-router-dom"
import { withAuthHandling, WithAuthHandling } from "../../WithAuthHandling"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { Button, createStyles, Link, Typography, WithStyles } from "@material-ui/core"
import * as React from "react"
import { ScrollableItem } from "../scrollable_items"
import Grid from "@material-ui/core/Grid"
import { withStyles } from "@material-ui/core/styles"
import { SavedNewsItem, UpsertSavedNewsItemResponse } from "../../news_room_api/saved_news_api"
import { StarBorderRounded } from "@material-ui/icons"
import AlternateLinks from "../alternate_links"
import { Api } from "../../Api"

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

export interface SavedNewsItemProps
    extends RouteComponentProps,
        WithAuthHandling,
        WithSnackbarProps,
        WithStyles<typeof styles> {
    saved_news_item: SavedNewsItem
    register_scrollable_item: (scrollable_item: ScrollableItem) => void
}

export interface SavedNewsItemState {
    is_saved: boolean
    saved_news_item_id: string
}

class SavedNewsItemView extends React.Component<SavedNewsItemProps, SavedNewsItemState> implements ScrollableItem {
    element: HTMLDivElement | null = null
    state: SavedNewsItemState = {
        is_saved: true,
        saved_news_item_id: this.props.saved_news_item.saved_news_item_id,
    }
    api: Api

    constructor(props: SavedNewsItemProps) {
        super(props)

        this.api = new Api(props)
        this.props.register_scrollable_item(this)
    }

    /* Scrollable Item methods */
    reportYPosition(): number {
        return this.element?.getBoundingClientRect().y || -1
    }

    scroll_to_top(): void {
        this.element?.scrollIntoView()
    }

    open_item(): void {
        document.open(this.props.saved_news_item.link, "_blank", "noopener")
    }

    toggleSavedItem(): void {
        if (this.state.is_saved) {
            this.api
                .delete(`/saved-news/${this.props.saved_news_item.saved_news_item_id}`, JSON.stringify({}))
                .catch((reason) => console.error(reason))
        } else {
            this.api
                .post<UpsertSavedNewsItemResponse>(
                    "/saved-news",
                    JSON.stringify({ news_item_id: this.props.saved_news_item.news_item_id })
                )
                .then((response) => this.setState({ saved_news_item_id: response[1].saved_news_item_id }))
                .catch((reason) => console.error(reason))
        }

        this.setState({ is_saved: !this.state.is_saved })
    }

    render(): JSX.Element {
        const { classes } = this.props
        const saved_news_item = this.props.saved_news_item
        const url = new URL(this.props.saved_news_item.link)
        const domain = url.hostname
        return (
            <Grid
                container
                className={classes.card}
                ref={(t): void => {
                    this.element = t
                }}
            >
                <Grid item xs={12} className={classes.cardTitle}>
                    <Link href={saved_news_item.link} className={classes.titleLink} target="_blank" rel="noopener">
                        <img src={saved_news_item.favicon} className={classes.domainIcon} alt={`[${domain}]`} />
                        {saved_news_item.title}
                    </Link>
                </Grid>
                <Grid item xs={12} className={classes.cardDescription}>
                    <div dangerouslySetInnerHTML={{ __html: saved_news_item.description }} />
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="subtitle2">
                        {saved_news_item.feed_title} / {saved_news_item.published}
                    </Typography>
                </Grid>
                <Grid item md={4} xs={12} className={classes.itemControlBar}>
                    <Button size="small" variant="text" onClick={(): void => this.toggleSavedItem()}>
                        <StarBorderRounded className={this.state.is_saved ? classes.savedIcon : classes.notSavedIcon} />
                    </Button>
                </Grid>
                <AlternateLinks
                    alternate_links={saved_news_item.alternate_links}
                    alternate_title_links={saved_news_item.alternate_title_links}
                    alternate_favicons={saved_news_item.alternate_favicons}
                />
                <div />
            </Grid>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(SavedNewsItemView))))
