import UserProfile from "./user/UserProfile";
import config from './Config'

export class ApiFetch {

    constructor(props) {
        this.props = props
        this.userProfile = UserProfile.load()
    }

    fetchAuthorized(endpoint, on_success) {
        const url = `${config.apihost}/${endpoint}`

        const request = new Request(url, {
            method: 'GET',
            headers: {
                'Authorization': this.userProfile.bearerToken,
                'Content-Type': 'application/json'
            }
        });
        fetch(request)
            .then(response => {
                if (response.status === 200) {
                    response.json().then(json => {
                        on_success(json)
                    })
                } else if (response.status === 401) {
                    this.props.history.push("/user/signin");
                    this.props.enqueueSnackbar('You need to signin again.', {
                        variant: 'warning',
                    });
                } else if (response.status === 403) {
                    this.props.history.push("/user/needs-approval");
                    this.props.enqueueSnackbar('Approval for usage is not yet given.', {
                        variant: 'warning',
                    });
                } else {
                    console.error(endpoint, response, response.statusText)
                    this.props.enqueueSnackbar(response.statusText, { variant: "error" })
                }
            })

    }
}