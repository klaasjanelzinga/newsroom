import UserProfile from "./user/UserProfile";
import config from './Config'
import {RouteComponentProps} from "react-router-dom";
import {WithSnackbarProps} from "notistack";
import {ErrorResponse} from "./user/model";

interface ApiProps extends WithSnackbarProps, RouteComponentProps {
}

export class Api {
    props: ApiProps
    userProfile: UserProfile | null

    constructor(props: ApiProps) {
        this.props = props
        this.userProfile = UserProfile.load()
    }

    static createBearerTokenFrom(id_token: string): string {
        return `Bearer ${id_token}`
    }


    _headers_from(id_token: string| null): Headers {
        const headers: HeadersInit = new Headers()
        headers.set('Content-Type', 'application/json')
        if (id_token) {
            headers.set("Authorization", Api.createBearerTokenFrom(id_token))
        }
        return headers;
    }

    async _parseResponse<T>(response: Response):Promise<T> {
        if (response.status === 401) {
            this.props.history.push(`/user/signin?redirect_to=${this.props.history.location.pathname}`);
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
        const bodyReason = await response.json() as ErrorResponse
        if (bodyReason?.detail)
            throw new Error(bodyReason.detail)
        throw new Error("Something in the request is wrong.")
    }

    async get<T>(endpoint: string): Promise<[number, T]> {

        if (!this.userProfile) {
            throw new Error("Unauthorized for authorized call")
        }
        const url = `${config.apihost}${endpoint}`

        const request = new Request(url, {
            method: 'GET',
            headers: this._headers_from(this.userProfile.id_token)
        });
        const response = await fetch(request)
        return [response.status, await this._parseResponse(response)]
    }

    async post<T>(endpoint: string, body: string| null = null, withToken: string | null = null): Promise<[number, T]> {
        if (!withToken && !this.userProfile) {
            throw new Error("Authorized call without authorization")
        }
        if (!withToken && this.userProfile) {
            withToken = this.userProfile.id_token
        }
        const url = `${config.apihost}${endpoint}`
        const response = await fetch(url, {
            headers: this._headers_from(withToken),
            method: "POST",
            body: body,
        })
        return [response.status, await this._parseResponse(response)]
    }
}