((d, w, c) => {

    const GET_USERS = async (uri) => {
        try {
            let request = await fetch(uri, {method: 'post'})
            let response = await request.json()
            HIDE_USERS_LOADER()
            await WRITE_USERS(response.data)
            SHOW_USERS_TABLE()
        } catch (e) {
            c.log(e)
        }
    }

    const WRITE_USERS = async (data) => {
        let table = d.querySelector('.users-table')
        let bodyTable = table.querySelector('tbody')
        bodyTable.textContent = ''
        data.map(item => {
            let tr = document.createElement('tr')
            let name_td = document.createElement('td')
            let parent_td = document.createElement('td')
            let age_td = document.createElement('td')
            let birthday_td = document.createElement('td')
            let phone_td = document.createElement('td')
            let address_td = document.createElement('td')
            let risk_td = document.createElement('td')
            name_td.textContent = item.instance
            parent_td.textContent = item.user
            birthday_td.textContent = item.birthday
            age_td.textContent = item.age
            address_td.textContent = item.address
            tr.appendChild(name_td)
            tr.appendChild(parent_td)
            tr.appendChild(age_td)
            tr.appendChild(birthday_td)
            tr.appendChild(phone_td)
            tr.appendChild(address_td)
            tr.appendChild(risk_td)
            bodyTable.appendChild(tr)
        })
    }

    const HIDE_USERS_LOADER = () => {
        let loader = d.querySelector('.users-loader')
        loader.style.display = 'none'
    }

    const SHOW_USERS_LOADER = () => {
        let loader = d.querySelector('.users-loader')
        loader.style.display = 'block'
    }

    const HIDE_USERS_TABLE = () => {
        let table = d.querySelector('.users-table')
        table.style.display = 'none'
    }

    const SHOW_USERS_TABLE = () => {
        let table = d.querySelector('.users-table')
        table.style.display = 'block'
    }


    w.addEventListener('load', async () => {
        const GROUP_CONTAINER = d.querySelector('#group-content')
        const GROUP_ID = GROUP_CONTAINER.dataset.groupId
        const DOMAIN =  window.location.origin
        const GET_USERS_URI = `${DOMAIN}/groups/${GROUP_ID}/get_users/`

        const MAIN = async () => {
            await GET_USERS(GET_USERS_URI)
        }

        await MAIN()
    })
})(document, window, console);
