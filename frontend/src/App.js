import logo from './logo.svg';
import './App.css';
import {useEffect, useState} from "react";

function Setlist({ setlistTitles, onSelect }) {
    return (
        <div>
            {setlistTitles.map((item, index) => (
                <h1 style={{cursor: 'pointer'}} onClick={() => console.log(`clicked ${item}`)}>{item}</h1>
            ))}
        </div>
    )
}

function AddNewSetlist({show, onNewSetlist}) {
    const defaultValues = {
        title: '',
    }

    const [values, setValues] = useState(defaultValues);

    if(!show) return <></>;

    const handleInputChange = (event) => {
        event.persist();

        setValues(() => ({
            ...values,
            title: event.target.value,
        }));
    };

    const addNewSetlist = (event) => {
        event.preventDefault();

        fetch('/new_setlist', {
            method: 'POST',
            headers: {
                "Content-Type": 'application/json',
            },
            body: JSON.stringify({'new_setlist': values.title}),
        }).then((response) => {
            if(response.ok && onNewSetlist != null) {
                onNewSetlist();
                setValues(defaultValues);
            }
        }).catch((error) => console.log(error));
    };

    return (
        <>
            <form onSubmit={addNewSetlist}>
                <label>
                    New Title
                    <input type="text" value={values.title} onChange={handleInputChange}/>
                </label>
            </form>
        </>
    )
}

function App() {
    const [currentScreen, setCurrentScreen] = useState(null);

    const [setlistTitles, setSetlistTitles] = useState([]);
    const [addNewSetlist, setAddNewSetlist] = useState(false)

    const [update, setUpdate] = useState(false);

    useEffect(() => {fetch('/setlists')
        .then((response) => response.json())
        .then((response) => {
            setSetlistTitles(() => {
                return response['result'];
            });
        });
    }, [update]);

    const handleOnNewSetlist = () => {
        setUpdate(!update);
        setAddNewSetlist(false);
    };

    return (
        <div className="App">
            <header className="App-header">
                <button onClick={() => setAddNewSetlist(!addNewSetlist)}>
                    Create new setlist
                </button>

                <AddNewSetlist show={addNewSetlist} onNewSetlist={handleOnNewSetlist} />
                <Setlist setlistTitles={setlistTitles} />
            </header>
        </div>
    );
}

export default App;
