import * as React from "react";
import {createStyles, Typography, WithStyles, withStyles} from "@material-ui/core";
import {NewsItem} from "../user/model";
import Grid from "@material-ui/core/Grid";
import Checkbox from "@material-ui/core/Checkbox";
import FormControlLabel from "@material-ui/core/FormControlLabel";

const styles = createStyles({
    header: {
        fontWeight: "bold"
    },
    card: {
        marginBottom: '2px',
        backgroundColor: '#efefef',
        justifyContent: 'left',
        padding: "10px"
    },
    cardRead: {
        marginBottom: '2px',
        backgroundColor: '#afafaf',
        justifyContent: 'left',
        padding: "10px",
        opacity: ".6"
    },
    cardDescription: {
        paddingTop: "7px",
    },
    cardTitle: {
        paddingTop: "3px",
        paddingBNottom: "4px",
    },
    titleLink: {
        fontSize: "large",
    },
    itemControlBar: {},
})

export interface NewsItemControl {
    scrollEvent: () => void
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

interface NewsItemProps extends WithStyles<typeof styles> {
    newsItem: NewsItem
    scrollEventRegistry: (newsItemControll: NewsItemControl) => void
    dynamicFetchRegistry: (newsItemDynamicFetchControl: NewsItemDynamicFetchControl) => void
}

interface NewsItemState {
    keepUnread: boolean
    isRead: boolean
    isReadStateIsSent: boolean
}


class NewsItemNode extends React.Component<NewsItemProps> implements NewsItemControl, NewsItemDynamicFetchControl {

    element: Element | null = null
    state: NewsItemState = {
        keepUnread: false,
        isRead: false,
        isReadStateIsSent: false,
    }

    constructor(props: NewsItemProps) {
        super(props);

        this.props.scrollEventRegistry(this)
        this.props.dynamicFetchRegistry(this)
        this.state.isRead = props.newsItem.is_read
    }

    isOutOfView() {
        if (this.element) {
            return this.element.getBoundingClientRect().y < 0
        }
        return false
    }

    isRead() {
        return this.state.isRead
    }

    scrollToTop() {
        this.element?.scrollIntoView()
    }

    reportYPosition() {
        if (this.element) {
            return this.element.getBoundingClientRect().y
        }
        return -1
    }

    newsItemId() {
        return this.props.newsItem.news_item_id
    }

    isReadStateIsSent() {
        return this.state.isReadStateIsSent
    }

    setIsReadStateIsSent(newValue: boolean) {
        this.setState({isReadStateIsSent: newValue})
    }

    scrollEvent = () => {
        if (this.element) {
            const rect = this.element.getBoundingClientRect()
            if (rect.y < 2) {
                this.markAsRead()
            }
        }
    }

    markAsRead() {
        if (!this.state.keepUnread) {
            this.setState({isRead: true})
        }
    }

    render() {
        const {classes} = this.props
        const newsItem = this.props.newsItem
        return <div>
            <Grid container
                  className={this.state.isRead ? classes.cardRead : classes.card}
                  ref={(t) => this.element = t}>
                <Grid item xs={12} className={classes.cardTitle}>
                    <a href={newsItem.link} className={classes.titleLink} target="_blank" rel="noopener noreferrer">{newsItem.title}</a>
                </Grid>
                <Grid item xs={12} className={classes.cardDescription}>
                    <div dangerouslySetInnerHTML={{__html: newsItem.description}}/>
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="subtitle2">
                        - {newsItem.feed_title} / {newsItem.published}
                    </Typography>
                </Grid>
                <Grid item xs={12} className={classes.itemControlBar}>
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={this.state.keepUnread}
                                onChange={() => this.setState({keepUnread: !this.state.keepUnread})}
                                name="keep_unread"
                                color="primary"
                            />
                        }
                        label="Keep unread"
                    />
                </Grid>
            </Grid>
        </div>
    }


}

export default withStyles(styles)(NewsItemNode)