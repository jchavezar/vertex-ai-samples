/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import Modal from './Modal';
import { useUI, useUser } from '@/lib/state';

export default function UserSettings() {
  const { name, info, setName, setInfo } = useUser();
  const { setShowUserConfig } = useUI();

  function updateClient() {
    setShowUserConfig(false);
  }

  return (
    <Modal onClose={() => setShowUserConfig(false)}>
      <div className="userSettings">
        <p>
          This is a simple tool that allows you to design, test, and banter with
          custom AI characters on the fly.
        </p>

        <form
          onSubmit={e => {
            e.preventDefault();
            setShowUserConfig(false);
            updateClient();
          }}
        >
          <p>Adding this optional info makes the experience more fun:</p>

          <div>
            <p>Your name</p>
            <input
              type="text"
              name="name"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="What do you like to be called?"
            />
          </div>

          <div>
            <p>Your info</p>
            <textarea
              rows={3}
              name="info"
              value={info}
              onChange={e => setInfo(e.target.value)}
              placeholder="Things we should know about you… Likes, dislikes, hobbies, interests, favorite movies, books, tv shows, foods, etc."
            />
          </div>

          <button className="button primary">Let’s go!</button>
        </form>
      </div>
    </Modal>
  );
}
