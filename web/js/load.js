var HOST  = 'http://10.100.35.121:5000/';
var URL = {
    events: HOST + 'api/events',
    rooms: HOST + 'api/rooms',
    people: HOST + 'api/people'
};

HOST = 'http://localhost:63342/junction_2k17/web/';
URL = {
    events: HOST + 'api/events',
    rooms: HOST + 'api/rooms',
    people: HOST + 'api/people'
};

// todo: cache data
// todo: add id to events

/*
- где чувак,
- кто в комнате
- историю по чуваку
- комнаты между которыми дольше всего ходят и т д
 */

function loadData(url, success) {
    return $.getJSON(url, success);
}

function getCamToRoomMap(roomsArray) {
    let map = {};
    for (let i = 0; i < roomsArray.length; ++i) {
        let cam_in = roomsArray[i]['cam_in'];
        let cam_out = roomsArray[i]['cam_out'];

        map[cam_in] = roomsArray[i]['id'];
        map[cam_out] = roomsArray[i]['id'];
    }
    return map;
}

function getCamToInOutMap(rooms) {
    let obj = {};
    for (let i = 0; i < rooms.length; ++i) {
        obj[rooms[i]['cam_in']] = 'cam_in';
        obj[rooms[i]['cam_out']] = 'cam_out';
    }
    return obj;
}

function getEventToPersonMap(events) {
    let obj = {};
    for (let i = 0; i < events.length; ++i) {
        obj[events[i]['id']] = events[i]['human'];
    }
    return obj;
}

function findById(id, array) {
    let result;
    for (let i = 0; i < array.length; ++i) {
        if (array[i]['id'] === id) {
            result = array[i];
            break;
        }
    }
    return result;
}

/**
 * Returns room, where the person was detected last time.
 *
 * @param {number} personId  person we're looking for
 * @return {Promise} object containing room
 */
function getLastPersonLocation(personId) {

    const events = loadData(URL.events);
    const rooms = loadData(URL.rooms);

    return Promise.all([events, rooms]).then(function (events, rooms) {
        let i, event, room;

        // getting last event related to personId
        for (i = events.length - 1; i >= 0; --i) {
            if (events[i]['human'] === personId) {
                event = events[i];
                break;
            }
        }

        // getting room, containing cam which have detected person
        if (event !== undefined) {
            const camId = event['cam'];
            for (i = 0; i < rooms.length; ++i) {
                if (rooms[i]['cam_in'] === camId ||
                    rooms[i]['cam_out'] === camId) {
                    room = rooms[i];
                }
            }
        }

        return room;
    })
}


function whoInTheRoom(roomId) {

    let process = function(rooms, events, people) {

        let resultSet = new Set();

        let eventToPersonMap = getEventToPersonMap(events);
        let camToRoomMap = getCamToRoomMap(rooms);
        let camToInOutMap = getCamToInOutMap(rooms);

        for (let i = 0; i < events.length; ++i) {

            let camId = events[i]['cam'];
            if (camToRoomMap[camId] ===  roomId) {

                let personId = eventToPersonMap[events[i]['id']];
                let person = findById(personId, people);

                let inOrOut = camToInOutMap[camId];
                if (inOrOut === 'cam_in') {
                    resultSet.add(person);
                } else if(inOrOut === 'cam_out') {
                    resultSet.delete(person);
                }
            }
        }

        return Array.from(resultSet);
    };

    let roomsPromise = loadData(URL.rooms);
    let eventsPromise = loadData(URL.events);
    let peoplePromise = loadData(URL.people);

    return Promise.all([roomsPromise, eventsPromise, peoplePromise]).then(process);

}


function personHistory(personId) {

    const events = loadData(URL.events);
    const rooms = loadData(URL.rooms);

    return Promise.all([events, rooms]).then(function (events, rooms) {
        let i, event, room;
        let result = [];

        let camToRoomMap = getCamToRoomMap();
        let camToInOutMap = getCamToInOutMap(rooms);

        for (i = events.length - 1; i >= 0; --i) {
            if (events[i]['human'] === personId) {
                let camId = events[i]['cam'];
                let inOrOut = camToInOutMap[camId];
                let roomId = camToRoomMap[camId];

                let obj = {
                    room: findById(rooms, roomId),
                    cam: inOrOut
                };

                result.push(obj);
            }
        }

        return result;
    })
}