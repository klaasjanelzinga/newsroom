import * as React from "react"
import { NewsItem } from "../news_room_api/news_item_api"
import { RouteComponentProps, withRouter } from "react-router-dom"
import { withAuthHandling, WithAuthHandling } from "../WithAuthHandling"
import { withSnackbar, WithSnackbarProps } from "notistack"
import { createStyles, WithStyles } from "@material-ui/core"
import { withStyles } from "@material-ui/core/styles"
import HeaderBar from "../headerbar/HeaderBar"
import Header from "../user/header"
import LinearProgress from "@material-ui/core/LinearProgress"

const styles = createStyles({
    newsRoot: {
        overflow: "hidden",
    },
    newsItems: {
        height: "99%",
        width: "100%",
        position: "fixed",
    },
    footer: {},
})

interface SavedNewsProps extends RouteComponentProps, WithAuthHandling, WithSnackbarProps, WithStyles<typeof styles> {}

interface SavedNewsState {
    saved_items: NewsItem[]
    is_loading: boolean
}

class SavedNews extends React.Component<SavedNewsProps, SavedNewsState> {
    state: SavedNewsState = {
        saved_items: [],
        is_loading: false,
    }

    render(): JSX.Element {
        const { classes } = this.props
        return (
            <div className={classes.newsRoot}>
                <HeaderBar />
                <Header title={"Saved News"} />
                {this.state.is_loading && <LinearProgress />}
            </div>
        )
    }
}

export default withStyles(styles)(withRouter(withSnackbar(withAuthHandling(SavedNews))))
