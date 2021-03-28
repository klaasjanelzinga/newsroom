import * as React from "react"
import { Button, createStyles, Link, Typography, WithStyles, withStyles } from "@material-ui/core"
import Grid from "@material-ui/core/Grid"
import Checkbox from "@material-ui/core/Checkbox"
import FormControlLabel from "@material-ui/core/FormControlLabel"
import AlternateLinks from "./alternate_links"
import { NewsItem } from "../news_room_api/news_item_api"
import RefreshIcon from "@material-ui/icons/Refresh"
import { Star, StarBorderRounded, StarHalfOutlined, StarOutline, StarOutlined, StarSharp } from "@material-ui/icons"
import { Api } from "../Api"
import { withAuthHandling, WithAuthHandling } from "../WithAuthHandling"
import { RouteComponentProps } from "react-router"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { withRouter } from "react-router-dom"
import { UpsertSavedNewsItemResponse } from "../news_room_api/saved_news_api"

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
        paddingBNottom: "4px",
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

export interface NewsItemControl {
    scrollEvent: (top_threshold: number) => void
    openLink: () => void
    markAsRead: () => void
    isRead: () => boolean
    isReadStateIsSent: () => boolean
    setIsReadStateIsSent: (newValue: boolean) => void
    newsItemId: () => string
    scrollToTop: () => void
    reportYPosition: () => number
}

export interface NewsItemDynamicFetchControl {
    isOutOfView: () => boolean
}

interface NewsItemProps extends WithAuthHandling, RouteComponentProps, WithSnackbarProps, WithStyles<typeof styles> {
    newsItem: NewsItem
    scrollEventRegistry: (newsItemControll: NewsItemControl) => void
    dynamicFetchRegistry: (newsItemDynamicFetchControl: NewsItemDynamicFetchControl) => void
}

interface NewsItemState {
    keepUnread: boolean
    isRead: boolean
    isSaved: boolean
    saved_news_item_id: string | null
    isReadStateIsSent: boolean
}

class NewsItemNode extends React.Component<NewsItemProps> implements NewsItemControl, NewsItemDynamicFetchControl {
    element: Element | null = null
    state: NewsItemState = {
        keepUnread: false,
        isRead: false,
        isSaved: this.props.newsItem.is_saved,
        saved_news_item_id: this.props.newsItem.saved_news_item_id,
        isReadStateIsSent: false,
    }
    api: Api

    constructor(props: NewsItemProps) {
        super(props)

        this.props.scrollEventRegistry(this)
        this.props.dynamicFetchRegistry(this)
        this.state.isRead = props.newsItem.is_read
        this.api = new Api(this.props)
    }

    isOutOfView(): boolean {
        if (this.element) {
            return this.element.getBoundingClientRect().y < 0
        }
        return false
    }

    isRead(): boolean {
        return this.state.isRead
    }

    scrollToTop(): void {
        this.element?.scrollIntoView()
    }

    reportYPosition(): number {
        if (this.element) {
            return this.element.getBoundingClientRect().y
        }
        return -1
    }

    newsItemId(): string {
        return this.props.newsItem.news_item_id
    }

    isReadStateIsSent(): boolean {
        return this.state.isReadStateIsSent
    }

    setIsReadStateIsSent(newValue: boolean): void {
        this.setState({ isReadStateIsSent: newValue })
    }

    scrollEvent = (top_threshold: number): void => {
        if (this.element) {
            const rect = this.element.getBoundingClientRect()
            if (rect.bottom < top_threshold) {
                this.markAsRead()
            }
        }
    }

    markAsRead(): void {
        if (!this.state.keepUnread) {
            this.setState({ isRead: true })
        }
    }

    toggleSavedItem(): void {
        if (this.props.newsItem.is_saved) {
            this.api
                .delete(`/saved-news/${this.state.saved_news_item_id}`, JSON.stringify({}))
                .catch((reason) => console.error(reason))
        } else {
            this.api
                .post<UpsertSavedNewsItemResponse>(
                    "/saved-news",
                    JSON.stringify({ news_item_id: this.props.newsItem.news_item_id })
                )
                .then((response) => this.setState({ saved_news_item_id: response[1].saved_news_item_id }))
                .catch((reason) => console.error(reason))
        }

        this.props.newsItem.is_saved = !this.props.newsItem.is_saved
        this.setState({ isSaved: !this.state.isSaved })
    }

    openLink(): void {
        document.open(this.props.newsItem.link, "_blank", "noopener")
    }

    render(): JSX.Element {
        const { classes } = this.props
        const newsItem = this.props.newsItem
        const url = new URL(newsItem.link)
        const domain = url.hostname
        return (
            <Grid
                container
                className={this.state.isRead ? classes.cardRead : classes.card}
                ref={(t): void => {
                    this.element = t
                }}
            >
                <Grid item xs={12} className={classes.cardTitle}>
                    <Link href={newsItem.link} className={classes.titleLink} target="_blank" rel="noopener">
                        <img src={newsItem.favicon} className={classes.domainIcon} alt={`[${domain}]`} />
                        {newsItem.title}
                    </Link>
                </Grid>
                <Grid item xs={12} className={classes.cardDescription}>
                    <div dangerouslySetInnerHTML={{ __html: newsItem.description }} />
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="subtitle2">
                        {newsItem.feed_title} / {newsItem.published}
                    </Typography>
                </Grid>
                <Grid item md={4} xs={12} className={classes.itemControlBar}>
                    <Button size="small" variant="text" onClick={() => this.toggleSavedItem()}>
                        <StarBorderRounded className={this.state.isSaved ? classes.savedIcon : classes.notSavedIcon} />
                    </Button>
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={this.state.keepUnread}
                                onChange={(): void => this.setState({ keepUnread: !this.state.keepUnread })}
                                name="keep_unread"
                                color="primary"
                            />
                        }
                        label="Keep unread"
                    />
                </Grid>
                <Grid item md={8} xs={12}>
                    <AlternateLinks newsItem={newsItem} />
                </Grid>
                <div />
            </Grid>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(NewsItemNode))))
