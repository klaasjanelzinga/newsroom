import UserProfile from "./user/UserProfile";
import config from './Config'
import {RouteComponentProps} from "react-router-dom";
import {WithSnackbarProps} from "notistack";

interface ApiFetchProps extends WithSnackbarProps, RouteComponentProps {
}

export class ApiFetch {
    props: ApiFetchProps
    userProfile: UserProfile | null

    constructor(props: ApiFetchProps) {
        this.props = props
        this.userProfile = UserProfile.load()
    }

    _headers_from(userProfile: UserProfile| null): Headers {
        const headers: HeadersInit = new Headers()
        headers.set('Content-Type', 'application/json')
        if (userProfile != null) {
            headers.set("Authorization", userProfile.bearerToken)
        }
        return headers;
    }

    async _parseResponse<T>(response: Response):Promise<T> {
        if (response.status === 401) {
            this.props.history.push("/user/signin");
            this.props.enqueueSnackbar('You need to signin again.', {
                variant: 'warning',
            });
        } else if (response.status === 403) {
            this.props.history.push("/user/needs-approval");
            this.props.enqueueSnackbar('Approval for usage is not yet given.', {
                variant: 'warning',
            });
        } else if (response.status === 200 || response.status === 201) {
            return await response.json() as T
        }
        throw new Error("Something in the request is wrong.")
    }

    async get<T>(endpoint: string): Promise<[number, T]> {

        const url = `${config.apihost}${endpoint}`

        const request = new Request(url, {
            method: 'GET',
            headers: this._headers_from(this.userProfile)
        });
        const response = await fetch(request)
        return [response.status, await this._parseResponse(response)]
    }

    async post<T>(endpoint: string, body: string| null = null, userProfile = this.userProfile): Promise<[number, T]> {
        const url = `${config.apihost}${endpoint}`
        const response = await fetch(url, {
            headers: this._headers_from(userProfile),
            method: "POST",
            body: body,
        })
        return [response.status, await this._parseResponse(response)]
    }
}